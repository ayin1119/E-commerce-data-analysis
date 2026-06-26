DROP TABLE IF EXISTS ml_window_config;

CREATE TABLE ml_window_config (
    dataset_type VARCHAR(20),
    snapshot_date DATE,
    feature_start_date DATE,
    feature_end_date DATE,
    label_start_date DATE,
    label_end_date DATE
);

INSERT INTO ml_window_config VALUES
('train', '2014-11-24', '2014-11-18', '2014-11-24', '2014-11-25', '2014-12-01'),
('valid', '2014-12-01', '2014-11-25', '2014-12-01', '2014-12-02', '2014-12-08'),
('test',  '2014-12-11', '2014-12-05', '2014-12-11', '2014-12-12', '2014-12-18');