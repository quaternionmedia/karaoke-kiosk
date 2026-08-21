"""queue_position and email_template table

Revision ID: 2_queue_and_email_templates
Revises: 575074851ec1
Create Date: 2026-06-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '2_queue_and_email_templates'
down_revision: Union[str, Sequence[str], None] = '575074851ec1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add queue_position to performance
    with op.batch_alter_table('performance', schema=None) as batch_op:
        batch_op.add_column(sa.Column('queue_position', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_performance_queue_position'), ['queue_position'], unique=False)

    # Create email_template table
    op.create_table('emailtemplate',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('venue_id', sa.Integer(), nullable=False),
        sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('subject', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('body', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('emailtemplate', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_emailtemplate_venue_id'), ['venue_id'], unique=False)
        batch_op.create_unique_constraint('uq_emailtemplate_venue_id_slug', ['venue_id', 'slug'])

    # Backfill email templates from existing venue columns
    connection = op.get_bind()
    venues = connection.execute(sa.text('SELECT id, email_subject_template, email_body_template FROM venue')).fetchall()
    
    for venue_id, subject_tpl, body_tpl in venues:
        # Only create if at least one template column is set
        if subject_tpl or body_tpl:
            connection.execute(
                sa.text('''
                    INSERT INTO emailtemplate 
                    (created_at, updated_at, venue_id, slug, name, subject, body, is_active)
                    VALUES 
                    (datetime('now'), datetime('now'), :venue_id, 'recording_share', 'Recording Share', 
                     COALESCE(:subject, 'Your performance at {venue}!'), 
                     COALESCE(:body, 'Hi {name}, here is your recording of {song}: {recording_url}'),
                     1)
                '''),
                {'venue_id': venue_id, 'subject': subject_tpl, 'body': body_tpl}
            )

    # Drop email template columns from venue (using batch_alter_table for SQLite compatibility)
    with op.batch_alter_table('venue', schema=None) as batch_op:
        batch_op.drop_column('email_subject_template')
        batch_op.drop_column('email_body_template')


def downgrade() -> None:
    # Recreate email template columns on venue
    with op.batch_alter_table('venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_subject_template', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
        batch_op.add_column(sa.Column('email_body_template', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    # Backfill venue columns from email_template table
    connection = op.get_bind()
    templates = connection.execute(
        sa.text('SELECT venue_id, subject, body FROM emailtemplate WHERE slug = :slug AND is_active = 1'),
        {'slug': 'recording_share'}
    ).fetchall()
    
    for venue_id, subject, body in templates:
        connection.execute(
            sa.text('UPDATE venue SET email_subject_template = :subject, email_body_template = :body WHERE id = :venue_id'),
            {'subject': subject, 'body': body, 'venue_id': venue_id}
        )

    # Drop email_template table
    op.drop_table('emailtemplate')

    # Remove queue_position from performance
    with op.batch_alter_table('performance', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_performance_queue_position'))
        batch_op.drop_column('queue_position')
