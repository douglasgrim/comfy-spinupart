import { app } from "../../scripts/app.js";

// Dynamic inputs for the SpinUpArt String Template node.
// Keeps exactly one empty INPUTn slot at the end: connecting to it adds a new
// slot, disconnecting removes the stale slot and renumbers the rest so the
// names stay contiguous (INPUT0, INPUT1, ...).

const TARGET_NODE = "SpinUpArtStringTemplate";
const PREFIX = "INPUT";
const DYNAMIC_TYPE = "*";

function isDynamicInput(input) {
    return input?.name?.startsWith(PREFIX);
}

function refreshDynamicInputs(node) {
    // Drop unconnected dynamic inputs (iterate backwards so indices stay valid).
    for (let i = node.inputs.length - 1; i >= 0; i--) {
        const input = node.inputs[i];
        if (isDynamicInput(input) && input.link == null) {
            node.removeInput(i);
        }
    }
    // Renumber the connected ones so templates can rely on {{INPUT0}}..{{INPUTn}}.
    let n = 0;
    for (const input of node.inputs) {
        if (isDynamicInput(input)) {
            input.name = `${PREFIX}${n}`;
            input.label = `${PREFIX}${n}`;
            n++;
        }
    }
    // Always leave one empty slot ready for the next connection.
    node.addInput(`${PREFIX}${n}`, DYNAMIC_TYPE);
    node.setSize(node.computeSize());
}

app.registerExtension({
    name: "spinupart.stringTemplate",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== TARGET_NODE) {
            return;
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated?.apply(this, arguments);
            if (!this.inputs?.some(isDynamicInput)) {
                this.addInput(`${PREFIX}0`, DYNAMIC_TYPE);
            }
            return result;
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (type, index, connected, linkInfo) {
            const result = onConnectionsChange?.apply(this, arguments);
            // Skip while a saved workflow is being restored: links arrive one at
            // a time and removing slots mid-restore would corrupt the graph.
            if (type === LiteGraph.INPUT && !app.configuringGraph) {
                refreshDynamicInputs(this);
            }
            return result;
        };
    },
});
