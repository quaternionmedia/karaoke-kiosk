import m from "mithril";
import * as api from "../api";

// ════════════════════════════════════════════════════════════════════
//  TEMPLATES VIEW
// ════════════════════════════════════════════════════════════════════

interface TemplatesViewState {
  venues: api.VenueRead[];
  templates: api.EmailTemplateRead[];
  selectedVenueId: number | null;
  editingTemplate: api.EmailTemplateRead | null;
  preview: { subject: string; body: string } | null;
  isLoading: boolean;
}

const ALLOWED_PLACEHOLDERS = ["name", "song", "recording_url", "venue"];

export const TemplatesView = {
  oninit: async (vnode: any) => {
    // Initialize vnode.state properly
    if (!vnode.state.venues) {
      Object.assign(vnode.state, {
        venues: [],
        templates: [],
        selectedVenueId: null,
        editingTemplate: null,
        preview: null,
        isLoading: false,
      });
    }
    const state = vnode.state as TemplatesViewState;

    state.isLoading = true;
    try {
      console.log("[Templates] Loading venues...");
      state.venues = await api.listVenues();
      console.log("[Templates] Loaded venues:", state.venues);
      if (state.venues.length > 0) {
        state.selectedVenueId = state.venues[0].id;
        console.log("[Templates] Loading templates for venue", state.selectedVenueId);
        state.templates = await api.listEmailTemplates(state.selectedVenueId);
        console.log("[Templates] Loaded templates:", state.templates);
      }
    } catch (e: any) {
      console.error("[Templates] Failed to load:", e);
      alert(`Failed to load templates: ${e.message || e}`);
    } finally {
      state.isLoading = false;
      m.redraw();
    }
  },

  view: (vnode: any) => {
    const state = vnode.state as TemplatesViewState;

    if (state.isLoading) {
      return m(".templates-view", "Loading...");
    }

    return m(".templates-view", [
      m("h2", "Email Templates"),

      // Venue picker
      m("div", [
        m("label", "Venue"),
        m(
          "select",
          {
            value: state.selectedVenueId || "",
            onchange: async (e: Event) => {
              const venueId = parseInt(
                (e.target as HTMLSelectElement).value,
                10
              );
              state.selectedVenueId = venueId;
              state.templates = await api.listEmailTemplates(venueId);
              state.editingTemplate = null;
              state.preview = null;
            },
          },
          state.venues.map((v) => m("option", { value: v.id }, v.name))
        ),
      ]),

      // Template list
      state.templates.length === 0
        ? m("p", "No templates for this venue")
        : m(
            "div",
            state.templates.map((template) =>
              m(
                ".template-item",
                {
                  class:
                    state.editingTemplate?.id === template.id ? "selected" : "",
                },
                [
                  m("h4", template.name),
                  m("p.template-slug", `Slug: ${template.slug}`),
                  m(
                    "button.btn.btn-sm",
                    {
                      onclick: () => {
                        state.editingTemplate = { ...template };
                        state.preview = null;
                      },
                    },
                    "Edit"
                  ),
                  m(
                    "button.btn.btn-sm",
                    {
                      onclick: async () => {
                        if (confirm("Delete this template?")) {
                          try {
                            await api.deleteEmailTemplate(template.id);
                            state.templates = state.templates.filter(
                              (t) => t.id !== template.id
                            );
                            state.editingTemplate = null;
                          } catch (e) {
                            alert("Failed to delete: " + e);
                          }
                        }
                      },
                    },
                    "Delete"
                  ),
                ]
              )
            )
          ),

      // Editor
      state.editingTemplate
        ? m(".template-editor", [
            m("h3", "Edit Template"),

            m("div", [
              m("label", "Name"),
              m("input", {
                type: "text",
                value: state.editingTemplate.name,
                oninput: (e: Event) => {
                  if (state.editingTemplate) {
                    state.editingTemplate.name = (e.target as HTMLInputElement)
                      .value;
                  }
                },
              }),
            ]),

            m("div", [
              m("label", "Subject"),
              m("input", {
                type: "text",
                value: state.editingTemplate.subject,
                oninput: (e: Event) => {
                  if (state.editingTemplate) {
                    state.editingTemplate.subject = (e.target as HTMLInputElement)
                      .value;
                  }
                },
              }),
            ]),

            m("div", [
              m("label", "Body"),
              m("textarea", {
                value: state.editingTemplate.body,
                oninput: (e: Event) => {
                  if (state.editingTemplate) {
                    state.editingTemplate.body = (e.target as HTMLTextAreaElement)
                      .value;
                  }
                },
              }),
            ]),

            // Placeholder chips
            m("div.placeholders", [
              m("label", "Available placeholders:"),
              m(
                "div",
                ALLOWED_PLACEHOLDERS.map((p) =>
                  m(".placeholder-chip", `{${p}}`)
                )
              ),
            ]),

            m(
              "button.btn.btn-primary",
              {
                onclick: async () => {
                  if (!state.editingTemplate) return;
                  try {
                    // Preview first to validate
                    state.preview = await api.previewEmailTemplate(
                      state.editingTemplate.id
                    );
                    // Then save
                    await api.updateEmailTemplate(
                      state.editingTemplate.id,
                      {
                        name: state.editingTemplate.name,
                        subject: state.editingTemplate.subject,
                        body: state.editingTemplate.body,
                      }
                    );
                    alert("Saved!");
                  } catch (e) {
                    alert("Failed to save: " + e);
                  }
                },
              },
              "Preview & Save"
            ),
          ])
        : null,

      // Preview
      state.preview
        ? m(".preview", [
            m("h4", "Preview"),
            m("div.preview-subject", [
              m("strong", "Subject: "),
              m("span", state.preview.subject),
            ]),
            m("div.preview-body", [
              m("strong", "Body:"),
              m("pre", state.preview.body),
            ]),
          ])
        : null,
    ]);
  },
};
