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



////////////////////////////////////////////////////////
// Define a time range
var startTime = processSs.getStartTime();
var endTime = processSs.getCurrentEndTime();
var stepSize = (endTime - startTime) / 100;  // Query in 10 steps

// Choose an example quark (first CPU core in the tree)
var exampleQuark = processSs.getQuarkAbsolute("CPUs", "0");  
print("\n--- Time Series for Quark " + exampleQuark + " ---");
for (var t = startTime; t <= endTime; t += stepSize) {
    var state = processSs.querySingleState(t, exampleQuark);
    print("Time " + t + " -> State: " + state);
}

