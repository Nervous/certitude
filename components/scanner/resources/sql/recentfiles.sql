--Table creation
CREATE TABLE recentfiles
(
	`computer_name` VARCHAR(384),
	`type` VARCHAR(384),
	`last_write_time` VARCHAR(384),
	`hive` VARCHAR(384),
	`key_path` VARCHAR(384),
	`attr_name` VARCHAR(384),
	`reg_type` VARCHAR(384),
	`attr_type` VARCHAR(384),
	`filename` VARCHAR(384)
);

.separator '	'
.import recentfiles.list recentfiles