CREATE UNIQUE INDEX uq_single_admin
ON users ((1))
WHERE role = 'ADMIN';