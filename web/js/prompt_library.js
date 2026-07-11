import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

const NODE_INFO = {
  PromptLibrary: {
    title: "Prompt Library",
    color: "#22395c",
    bgcolor: "#17263e",
    help: "Wybierz folder, kategorię i tryb. Wyjścia Positive oraz Negative podłącz do odpowiednich enkoderów tekstu.",
  },
  PL_PromptBuilder: {
    title: "Prompt Library / Builder",
    color: "#4a3267",
    bgcolor: "#2d1e40",
    help: "Opcjonalnie łączy bazę i kilka fragmentów promptu w jeden tekst.",
  },
  PromptValidator: {
    title: "Prompt Library / Doctor",
    color: "#245d59",
    bgcolor: "#173d3a",
    help: "Najpierw wybierz action = diagnose. Bezpieczne naprawy tworzą kopię w .promptlibrary_backups.",
  },
  PromptLibraryUtilities: {
    title: "Prompt Library / Utilities",
    color: "#6a4a23",
    bgcolor: "#422f19",
    help: "Reload Library po zapisaniu zmian w plikach TXT oraz reset historii trybu Unique.",
  },
  PL_PromptPreview: {
    title: "Prompt Library / Preview",
    color: "#31556e",
    bgcolor: "#1e3545",
    help: "Podłącz Positive, a opcjonalnie także Negative i Debug. Wynik pojawi się bezpośrednio w node.",
  },
};

function infoFor(node) {
  return NODE_INFO[node?.comfyClass] || NODE_INFO[node?.type];
}

function showHelp(node) {
  const info = infoFor(node);
  if (!info) return;
  const toast = app?.extensionManager?.toast;
  if (toast?.add) {
    toast.add({ severity: "info", summary: info.title, detail: info.help, life: 10000 });
    return;
  }
  window.alert(`${info.title}\n\n${info.help}`);
}

function helpMenuItem(node) {
  return { content: "PromptLibrary — szybka pomoc", callback: () => showHelp(node) };
}

function ensurePreviewWidget(node) {
  if (node.__plPreviewWidget) return node.__plPreviewWidget;

  try {
    const created = ComfyWidgets.STRING(
      node,
      "prompt_preview",
      ["STRING", { multiline: true, default: "Uruchom workflow, aby zobaczyć podgląd." }],
      app,
    );
    const widget = created.widget;
    widget.serialize = false;
    if (widget.inputEl) {
      widget.inputEl.readOnly = true;
      widget.inputEl.style.minHeight = "260px";
      widget.inputEl.style.fontFamily = "monospace";
      widget.inputEl.style.whiteSpace = "pre-wrap";
    }
    node.__plPreviewWidget = widget;
    node.setSize([Math.max(node.size[0], 430), Math.max(node.size[1], 430)]);
    return widget;
  } catch (error) {
    const widget = node.addWidget(
      "text",
      "prompt_preview",
      "Uruchom workflow, aby zobaczyć podgląd.",
      () => {},
      { multiline: true },
    );
    widget.serialize = false;
    node.__plPreviewWidget = widget;
    node.setSize([Math.max(node.size[0], 430), Math.max(node.size[1], 430)]);
    return widget;
  }
}

app.registerExtension({
  name: "PromptLibrary.UXFoundation",

  nodeCreated(node) {
    const info = infoFor(node);
    if (!info) return;
    node.color = info.color;
    node.bgcolor = info.bgcolor;
    if (node.comfyClass === "PL_PromptPreview" || node.type === "PL_PromptPreview") {
      ensurePreviewWidget(node);
    }
    node.setDirtyCanvas?.(true, true);
  },

  getNodeMenuItems(node) {
    if (!infoFor(node)) return [];
    return [null, helpMenuItem(node)];
  },

  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (!NODE_INFO[nodeData?.name]) return;

    const originalMenu = nodeType.prototype.getExtraMenuOptions;
    nodeType.prototype.getExtraMenuOptions = function (_, options) {
      originalMenu?.apply(this, arguments);
      const alreadyPresent = options.some((item) => item?.content === "PromptLibrary — szybka pomoc");
      if (!alreadyPresent) options.push(null, helpMenuItem(this));
    };

    if (nodeData.name === "PL_PromptPreview") {
      const originalCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () {
        const result = originalCreated?.apply(this, arguments);
        ensurePreviewWidget(this);
        return result;
      };

      const originalExecuted = nodeType.prototype.onExecuted;
      nodeType.prototype.onExecuted = function (message) {
        originalExecuted?.apply(this, arguments);
        const widget = ensurePreviewWidget(this);
        const text = Array.isArray(message?.text) ? message.text[0] : message?.text;
        if (typeof text === "string") {
          widget.value = text;
          widget.inputEl?.dispatchEvent(new Event("input", { bubbles: true }));
          this.setDirtyCanvas?.(true, true);
        }
      };
    }
  },
});
