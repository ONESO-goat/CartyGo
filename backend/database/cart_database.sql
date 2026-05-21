

create table if not exists cart_coordinates (
    id serial primary key,
    x integer not null,
    y integer not null
);

create table if not exists cart_items (
    id serial primary key,
    name text not null,
    quantity integer not null
);

create table if not exists cart (
    id serial primary key,
    item_id integer references cart_items(id),
    home_coordinates_id integer references cart_coordinates(id),
    previous_addresses text[]
);

