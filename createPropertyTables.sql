SET AUTOCOMMIT=ON;

select 'dropping table porperties';
drop table if exists porperties;

select 'creating table porperties';
create table porperties (
  listNo    bigint,
  name       varchar(255),
  ownship    varchar(255),
  area 	     varchar(255),
  udtmNprice varchar(255),
  topYear    int,
  nearestMrt varchar(255)
) with (engine=brighthouse);


\quit




