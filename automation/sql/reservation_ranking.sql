-- CTE + aggregation + a window function. Tied totals share the same rank.
WITH customer_totals AS (
    SELECT email, SUM(quantity) AS units
    FROM reservations
    WHERE status = 'active'
    GROUP BY email
)
SELECT email, units, DENSE_RANK() OVER (ORDER BY units DESC) AS position
FROM customer_totals
ORDER BY units DESC, email;
