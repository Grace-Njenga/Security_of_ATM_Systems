RENAME TABLE users TO bank_users;
ALTER TABLE bank_users DROP COLUMN email;
ALTER TABLE bank_users ADD PRIMARY KEY (account_number), ADD UNIQUE (national_id);
ALTER TABLE bank_users MODIFY otp INT NOT NULL;
ALTER TABLE bank_users MODIFY national_id INT NOT NULL;
ALTER TABLE bank_users ADD COLUMN otp_expiry DATETIME;
ALTER TABLE bank_users DROP COLUMN otp_expiry;
ALTER TABLE bank_users ADD COLUMN otp_expiry DATETIME;
ALTER TABLE bank_users ADD COLUMN face_encoding BLOB;
ALTER TABLE bank_users ADD COLUMN verify_encoding BLOB;
ALTER TABLE bank_users
ADD COLUMN acc_balance INT AFTER national_id;
ALTER TABLE bank_users MODIFY account_number VARCHAR(20);

ALTER TABLE bank_users
ADD COLUMN email VARCHAR(100) AFTER acc_balance;

ALTER TABLE bank_users MODIFY otp INT NULL;

ALTER TABLE bank_users
ALTER COLUMN acc_balance SET DEFAULT 0;

CREATE TABLE transactions (
    transaction_id INT NOT NULL,
    transaction_date DATETIME,
    transaction_type VARCHAR(255) NOT NULL,
    transaction_amount DECIMAL(10, 2),
    account_number VARCHAR(20),
    PRIMARY KEY (transaction_id),
    FOREIGN KEY (account_number) REFERENCES bank_users (account_number)
);

CREATE TABLE verify_face_db (
    face_id INT AUTO_INCREMENT ,
    face_image LONGBLOB,
    face_embedding BLOB,
    account_number VARCHAR(20),
    PRIMARY KEY (face_id),
    FOREIGN KEY (account_number) REFERENCES bank_users (account_number)
);
--- when you want to drop a table that has been linked to another table --
ALTER TABLE face_db
DROP FOREIGN KEY account_number;
DROP TABLE face_db;
--- some minor corrections---
ALTER TABLE bank_users DROP COLUMN face_encoding;
ALTER TABLE bank_users DROP COLUMN verify_encoding;
