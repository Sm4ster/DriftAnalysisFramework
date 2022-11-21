// db.js
import Dexie from 'dexie';

export const db = new Dexie('DriftAnalysis');
db.version(1).stores({
  runs: "uuid", // Primary key and indexed props
  locations: "uuid, location_id, run_id, vector",
});