--Table creation
CREATE TABLE process
(
	`pid` INT PRIMARY KEY NOT NULL
	`name` VARCHAR(384),
	`command` VARCHAR(384),
	`path` VARCHAR(384)
);

.separator '	'
.import process.list process