const NO_IBTN = "_NO_IBUTTON_";
export const ibuttonAlias = Object.freeze({
  "0169F9060100009F": "Llavero 1",
  "0168FD2701000048": "Llavero 2",
  "0197E81801000062": "Llavero 3",
  "01AAF92601000029": "Llavero 4",
  "01C44B1A0100006F": "Llavero 5",
  "6F0000011A4BC401": "Llavero 5",

  "0146FF1901000033": "Llavero Negro",
  "3300000119FF4601": "Llavero Negro",

  "016E818A01000082": "Llavero Verde",
  "820000018A816E01": "Llavero Verde",

  "0173E22601000077": "Llavero Rojo Nuevo",
  "7700000126E27301": "Llavero Rojo Nuevo",

  "01884C890100005F": "Llavero Verde Nuevo",
  "5F000001894C8801": "Llavero Verde Nuevo",

  "01FB132801000042": "Llavero Azul",
  "420000012813FB01": "Llavero Azul",

  "017B0C14010000E1": "Llavero Rojo",
  "E1000001140C7B01": "Llavero Rojo",

  "2900000126F9AA01": "Jaime Benavides",
  [NO_IBTN]: "Sin iButton",
});

export function ibuttonNickname(value) {
  const key = String(value ?? '').trim().toUpperCase();
  if (!key || ['N/A', 'NONE', 'NULL', '_NO_IBUTTON_'].includes(key)) return 'Sin iButton';
  return Object.prototype.hasOwnProperty.call(ibuttonAlias, key) ? ibuttonAlias[key] : 'Sin apodo';
}
