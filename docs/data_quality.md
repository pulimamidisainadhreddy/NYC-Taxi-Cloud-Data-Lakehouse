# Data Quality

Checks:
- required columns
- pickup/drop-off timestamps
- drop-off not earlier than pickup
- non-negative distance
- non-negative fare/total amount according to the business rule
- non-negative passenger count
- populated location IDs
- duplicate control
- dbt not-null/unique tests
- custom SQL business tests

Invalid rows are written to the rejected layer with a rejection reason. Production extensions should persist check results to a control/metrics table.
