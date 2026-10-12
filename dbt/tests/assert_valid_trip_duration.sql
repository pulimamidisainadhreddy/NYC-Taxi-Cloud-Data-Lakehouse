select * from {{ ref('fct_trips') }} where trip_duration_minutes < 0
