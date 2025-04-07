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

////////////////////////////////////////////////////////
var startTime = processSs.getStartTime();
var endTime = processSs.getCurrentEndTime();
// Choose a timestamp in the middle so that the state system is fully built
var midTime = Math.floor((startTime + endTime) / 2);
print("Using midTime = " + midTime);
try {
    // Get the root "CPUs" node
    var cpusRoot = processSs.getQuarkAbsolute("CPUs");
    // Get all leaf nodes under "CPUs" (assuming two levels deep hold the data)
    var cpuLeafQuarks = processSs.getQuarks(cpusRoot, "*", "*");

    // Compute a mid-range timestamp
    var startTime = processSs.getStartTime();
    var endTime = processSs.getCurrentEndTime();
    var midTime = Math.floor((startTime + endTime) / 2);
    print("Using midTime = " + midTime);

    // Define a larger interval: here, 1 second (1e9 nanoseconds)
    var delta = 1000000000; // 1,000,000,000 ns = 1 second
    var startRange = midTime;
    var endRange = midTime + delta;
    
    // Perform the 2D query on the list of leaf quarks.
    // query2D returns a Java List of intervals.
    var intervalsList = processSs.query2D(cpuLeafQuarks, startRange, endRange);
    // Get an iterator from the Java List.
    var iter = intervalsList.iterator();

    print("2D query results for leaf nodes under 'CPUs' between " + startRange + " and " + endRange + ":");
    while (iter.hasNext()) {
         var interval = iter.next();
         var q = interval.getAttribute();
         var fullPath = processSs.getFullAttributePath(q);
         var value = interval.getStateValue();
         // Only print if the state value is meaningful (i.e. not null or a null marker)
         if (value != null && value.toString().indexOf("nullValue") < 0) {
             print("  " + fullPath + " => " + value);
         }
    }
} catch (e) {
    print("Error during revised 2D query: " + e);
}




