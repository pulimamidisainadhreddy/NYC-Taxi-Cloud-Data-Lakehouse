
{{ config(materialized='table') }}
select * from {{ ref('stg_yellow_taxi') }}
