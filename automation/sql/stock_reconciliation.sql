-- Available stock + active reservations must equal the initial stock.
-- LEFT JOIN keeps products that have no reservations.
SELECT p.sku, p.stock,
       COALESCE(SUM(CASE WHEN r.status = 'active' THEN r.quantity ELSE 0 END), 0) AS reserved,
       p.stock + COALESCE(SUM(CASE WHEN r.status = 'active' THEN r.quantity ELSE 0 END), 0) AS total
FROM products AS p
LEFT JOIN reservations AS r ON r.sku = p.sku
GROUP BY p.sku, p.stock
ORDER BY p.sku;
