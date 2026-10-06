// Everything said on screen comes from the site catalog (read at build time). Never hardcode a price.
import launch from "../../site/catalog/launch.json";

type Colour = { name: string; tier: string; hex: string; metal: number; rough: number };
const L = launch as unknown as {
  colors: Colour[];
  prices: Record<string, string>;
  cars: { id: string; make: string; model: string; generation: string }[];
  headlights: { surcharge: string; values: { name: string; hex: string; base?: boolean }[] };
  wall: { prices: Record<string, string>; items: { id: string; make: string; model: string; generation: string }[] };
  extras: { items: { id: string; price: string; size_mm: number[] }[] };
};

const minPrice = (p: Record<string, string>) => Math.min(...Object.values(p).map(Number)).toFixed(2);

export const COLOURS = L.colors;
export const colour = (name: string) => {
  const c = L.colors.find((x) => x.name.toLowerCase() === name.toLowerCase());
  if (!c) throw new Error(`colour ${name} not in launch.json`);
  return c;
};
export const N_CARS = L.cars.length;
export const N_COLOURS = L.colors.length;
export const FROM = `$${minPrice(L.prices)}`;
export const WALL_FROM = `$${minPrice(L.wall.prices)}`;
export const N_WALL = L.wall.items.length;
export const WALL_IDS = L.wall.items.map((w) => w.id);
export const HEADLIGHT_SURCHARGE = `+$${L.headlights.surcharge}`;
export const headlight = (name: string) => {
  const h = L.headlights.values.find((x) => x.name.toLowerCase() === name.toLowerCase());
  if (!h) throw new Error(`headlight ${name} not in launch.json`);
  return h.hex;
};
const spinner = (id: string) => {
  const x = L.extras.items.find((i) => i.id === `${id}_spinner`);
  if (!x) throw new Error(`${id}_spinner missing from launch.json`);
  return { price: `$${x.price}`, size: `About ${Math.round(x.size_mm[0])} × ${Math.round(x.size_mm[1])} mm` };
};
export const KARAMBIT = spinner("karambit");
export const SHIELD = spinner("shield");
const talon = L.extras.items.find((x) => x.id === "talon_spinner");
if (!talon) throw new Error("talon_spinner missing from launch.json");
export const TALON_PRICE = `$${talon.price}`;
export const TALON_SIZE = `${Math.round(talon.size_mm[0])} × ${Math.round(talon.size_mm[1])} mm`;
export const carName = (id: string) => {
  const c = L.cars.find((x) => x.id === id) ?? L.wall.items.find((x) => x.id === id);
  return c ? `${c.make} ${c.model} (${c.generation})` : id;
};
