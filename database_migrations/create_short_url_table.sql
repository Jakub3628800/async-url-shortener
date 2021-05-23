--Manually written sql migrations.
create table short_urls(
url_key varchar(256) primary key,
target text
);