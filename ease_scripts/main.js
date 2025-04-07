// Load required modules for Trace Compass
loadModule("/TraceCompass/Trace");    // For trace-related helper functions
loadModule("/TraceCompass/Analysis"); // For analysis-related helper functions
loadModule("/System/Resources");      // For standard EASE resource functions

// Get the active trace (assumes one is already open)
var trace = getActiveTrace();

// Define the analysis ID for CPU usage (depends on the trace type)
var processAnalysisId = "org.eclipse.tracecompass.analysis.os.linux.cpuusage";

// Retrieve the analysis object for the given trace
var processAnalysis = getTraceAnalysis(trace, processAnalysisId);

// Schedule and execute the analysis
processAnalysis.schedule();
processAnalysis.waitForCompletion();

// Retrieve the state system associated with the analysis
var processSs = processAnalysis.getStateSystem();
print("State System Object: " + processSs);

// Print basic state system details
print("CPU Usage Attribute Tree: " + processSs.getAttributeTree());
print("State System Start Time: " + processSs.getStartTime());
print("State System End Time: " + processSs.getCurrentEndTime());
print("Total Number of Attributes: " + processSs.getNbAttributes());

// Fetch all quarks manually
var allQuarks = [];
for (var i = 0; i < processSs.getNbAttributes(); i++) {
    allQuarks.push(i);
}
print("All Quarks Found: " + allQuarks);

// Debugging: Print first 10 attributes for validation
print("\n--- Sample Quarks and Their Paths ---");
for (var i = 0; i < Math.min(10, processSs.getNbAttributes()); i++) { 
    var name = processSs.getAttributeName(i);
    var fullPath = processSs.getFullAttributePath(i);
    print("Quark " + i + ": " + name + " (Full Path: '" + fullPath + "')");
}

// Function to print the full attribute tree using known quarks
function printAttributeTree(ss, allQuarks) {
    var quarkToChildren = {};  // Store child relationships

    // Build a mapping of parents to children
    for (var i = 0; i < allQuarks.length; i++) {
        var quark = allQuarks[i];
        var parentQuark = ss.getParentAttributeQuark(quark);
        
        if (parentQuark != -1) { // Ignore root level attributes
            if (!(parentQuark in quarkToChildren)) {
                quarkToChildren[parentQuark] = [];
            }
            quarkToChildren[parentQuark].push(quark);
        }
    }

    // Recursive function to print attributes
    function traverseTree(quark, indent) {
        var name = ss.getAttributeName(quark);
        var fullPath = ss.getFullAttributePath(quark);
        print(indent + "Quark " + quark + ": " + name + " (Full Path: '" + fullPath + "')");

        if (quark in quarkToChildren) {
            for (var i = 0; i < quarkToChildren[quark].length; i++) {
                traverseTree(quarkToChildren[quark][i], indent + "  ");
            }
        }
    }

    // Start traversal from the root quarks
    print("\n--- Full Attribute Tree ---");
    for (var i = 0; i < allQuarks.length; i++) {
        var parentQuark = ss.getParentAttributeQuark(allQuarks[i]);
        if (parentQuark == -1) { // Root level attributes
            traverseTree(allQuarks[i], "");
        }
    }
}

// Print the full attribute tree
printAttributeTree(processSs, allQuarks);
