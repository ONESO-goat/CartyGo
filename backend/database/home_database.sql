create table home(
    id serial primary key,
    x integer not null,
    y integer not null,
    store_name text not null,
    store_address text not null,

    connected_carts text[]
);