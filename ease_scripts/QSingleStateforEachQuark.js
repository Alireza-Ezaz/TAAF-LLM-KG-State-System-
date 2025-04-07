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


// --------------------------------------------------------------------------------
// 1) Ensure you've loaded the modules and obtained the state system (processSs)
//    from your CPU usage analysis, as in your existing script:
// --------------------------------------------------------------------------------

// Example: define a timestamp (in ns) somewhere between startTime and endTime
var startTime = processSs.getStartTime();
var endTime   = processSs.getCurrentEndTime();
var midTime   = (startTime + endTime) / 2;  // just as an example

print("Start = " + startTime + ", End = " + endTime + ", Query Time = " + midTime);

// --------------------------------------------------------------------------------
// 2) Query single state for each quark at 'midTime'
// --------------------------------------------------------------------------------
var nbAttributes = processSs.getNbAttributes();

for (var q = 0; q < nbAttributes; q++) {
    var interval = processSs.querySingleState(midTime, q);
    var val      = interval.getStateValue(); // ITmfStateValue
    var path     = processSs.getFullAttributePath(q);

    // Check if the value is null or not
    if (!val.isNull()) {
        // For CPU usage attributes, typical values are integers or long
        // But you should always check the type to be safe
        var valueType = val.getType(); // returns an enum: INTEGER, LONG, DOUBLE, STRING, NULL, etc.
        var valueStr  = val.toString(); // or val.unboxValue() in newer versions
        print("Quark " + q + " ('" + path + "') => " +
              "Interval [" + interval.getStartTime() + ", " + interval.getEndTime() + "], " +
              "Value: " + valueStr + " (Type: " + valueType + ")");
    } else {
        print("Quark " + q + " ('" + path + "') => State is NULL at t=" + midTime);
    }
}




