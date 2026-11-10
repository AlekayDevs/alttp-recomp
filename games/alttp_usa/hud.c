/* A Link to the Past (USA): the "LIFE" label of the status bar says "VIDA" with language = es.
 *
 * The label is two tiles of the BG3 sheet, two letters each ("LI" and "FE": tiles $AB and $AC from word $7000 of the VRAM), which come
 * from compressed graphics, so they are changed in the VRAM and not in the ROM. alttp_wide_fill (widefill.c, the hook at 00:80B5, once
 * per frame) calls alttp_hud_poll: where the two tiles are
 * the ones of "LI" and "FE" (drawn here from the shape of their letters, not read from the game) they are replaced by "VI" and "DA";
 * on any other screen the tiles hold something else and nothing is touched.
 *
 * The same poll does the four labels of the pause menu (ITEM, DO, PENDANTS, EQUIPMENT; see alttp_pause_labels at the end). */
#include <string.h>
#include "snes_rt.h"

void alttp_pause_labels(void);

#define TILE_LI 0x7558u /* word address of tile $AB of the sheet at $7000 */
#define TILE_FE 0x7560u /* tile $AC */

/* Letters of 6 rows by 3 columns at most; the status bar font gives each body pixel a shadow to its right and below. */
typedef struct { char ch; const char *rows[6]; } Letter;
static const Letter letters[] = {
    { 'L', { "o..", "o..", "o..", "o..", "o..", "ooo" } }, { 'I', { "o", "o", "o", "o", "o", "o" } },
    { 'F', { "ooo", "o..", "ooo", "o..", "o..", "o.." } }, { 'E', { "ooo", "o..", "ooo", "o..", "o..", "ooo" } },
    { 'V', { "o.o", "o.o", "o.o", "o.o", ".o.", ".o." } }, { 'D', { "oo.", "o.o", "o.o", "o.o", "o.o", "oo." } },
    { 'A', { ".o.", "o.o", "o.o", "ooo", "o.o", "o.o" } },
};

/* The 8 rows (two bitplanes each) of a tile with letter `a` at column `ca` and letter `b` at column `cb`, body in colour 2, shadow in 3. */
static void draw(char a, int ca, char b, int cb, uint16_t out[8]) {
    int grid[9][9] = { { 0 } }, n, r, c, k;
    char which[2] = { a, b };
    int col[2] = { ca, cb };
    for (k = 0; k < 2; k++)
        for (n = 0; n < (int)(sizeof letters / sizeof letters[0]); n++) {
            if (letters[n].ch != which[k]) continue;
            for (r = 0; r < 6; r++)
                for (c = 0; letters[n].rows[r][c]; c++)
                    if (letters[n].rows[r][c] == 'o') grid[r][col[k] + c] = 2;
        }
    for (r = 0; r < 8; r++)
        for (c = 0; c < 8; c++)
            if (grid[r][c] == 2) {
                if (!grid[r][c + 1]) grid[r][c + 1] = 3;
                if (!grid[r + 1][c]) grid[r + 1][c] = 3;
                if (!grid[r + 1][c + 1]) grid[r + 1][c + 1] = 3;
            }
    for (r = 0; r < 8; r++) {
        unsigned lo = 0, hi = 0;
        for (c = 0; c < 8; c++) {
            lo |= (unsigned)(grid[r][c] & 1) << (7 - c);
            hi |= (unsigned)(grid[r][c] >> 1) << (7 - c);
        }
        out[r] = (uint16_t)(lo | hi << 8);
    }
}

static int is_tile(uint32_t at, const uint16_t want[8]) {
    int r;
    for (r = 0; r < 8; r++) if (ppu_vram_read16((uint16_t)(at + (uint32_t)r)) != want[r]) return 0;
    return 1;
}

void alttp_hud_poll(void) {
    uint16_t li[8], fe[8], vi[8], da[8];
    int r;
    if (game_opt("language", 0) != 1 || !game_opt("hud_text", 1)) return; /* hud_text=0: the tests that compare pictures keep the label as it is */
    alttp_pause_labels();
    draw('L', 1, 'I', 5, li);
    draw('F', 0, 'E', 4, fe);
    if (!is_tile(TILE_LI, li) || !is_tile(TILE_FE, fe)) return;
    draw('V', 1, 'I', 5, vi);
    draw('D', 0, 'A', 4, da);
    for (r = 0; r < 8; r++) {
        ppu_vram_write16((uint16_t)(TILE_LI + (uint32_t)r), vi[r]);
        ppu_vram_write16((uint16_t)(TILE_FE + (uint32_t)r), da[r]);
    }
}

/* ---- the labels of the pause menu ----
 *
 * ITEM, DO, PENDANTS and EQUIPMENT are drawn in the top or left edge of their boxes with tiles of the BG3 sheet (word $7000 of the VRAM) that come
 * from compressed graphics, in a small font of letters 3 pixels wide: each label is some tiles of 8x8 pixels, the letters in colour 2 on rows 1 to 5 and
 * colour 3 around. The game builds their tilemap in the WRAM (the first tile of each is at $1146, $1546, $132C and $15AC, with the words $246E,
 * $2482, $2521 and $2479; the attribute byte also has bit 8 of the tile number), so that is what tells that the pause menu is up (module $0E). Then the tiles are drawn again here with the Spanish
 * words in a font of the same size (nothing is read from the ROM's graphics: only the shape of the label is: where a tile is the ROM's own, its
 * first and last rows stay) and the map entries of the longer ones are pointed at tiles that the screen leaves empty. */

#define BG3_SHEET 0x7000u
#define BG3_MAP 0x6800u /* the bottom left quarter of the 64x64 map of BG3, where the menu is */

static const char *const glyph_rows[26][5] = {
    { ".o.", "o.o", "ooo", "o.o", "o.o" }, { "oo.", "o.o", "oo.", "o.o", "oo." }, { ".oo", "o..", "o..", "o..", ".oo" },
    { "oo.", "o.o", "o.o", "o.o", "oo." }, { "ooo", "o..", "oo.", "o..", "ooo" }, { "ooo", "o..", "oo.", "o..", "o.." },
    { ".oo", "o..", "o.o", "o.o", ".oo" }, { "o.o", "o.o", "ooo", "o.o", "o.o" }, { "o", "o", "o", "o", "o" },
    { "..o", "..o", "..o", "o.o", ".o." }, { "o.o", "o.o", "oo.", "o.o", "o.o" }, { "o..", "o..", "o..", "o..", "ooo" },
    { "o.o", "ooo", "ooo", "o.o", "o.o" }, { "oo.", "o.o", "o.o", "o.o", "o.o" }, { ".o.", "o.o", "o.o", "o.o", ".o." },
    { "oo.", "o.o", "oo.", "o..", "o.." }, { ".o.", "o.o", "o.o", "ooo", ".oo" }, { "oo.", "o.o", "oo.", "o.o", "o.o" },
    { ".oo", "o..", ".o.", "..o", "oo." }, { "ooo", ".o.", ".o.", ".o.", ".o." }, { "o.o", "o.o", "o.o", "o.o", "ooo" },
    { "o.o", "o.o", "o.o", "o.o", ".o." }, { "o.o", "o.o", "ooo", "ooo", "o.o" }, { "o.o", "o.o", ".o.", "o.o", "o.o" },
    { "o.o", "o.o", ".o.", ".o.", ".o." }, { "ooo", "..o", ".o.", "o..", "ooo" },
};

/* `n` tiles of a label: `text` in colour 2 on colour 3, rows 1 to 5 (the other rows of a tile are colour 3, as in the game's), as 8 words per tile. */
static void label_tiles(const char *text, int n, uint16_t *out) {
    uint8_t px[5 * 8][8];
    int x = 0, t, r, c, k;
    memset(px, 3, sizeof px);
    for (k = 0; text[k]; k++) {
        const char *const *g = glyph_rows[text[k] - 'A'];
        for (r = 0; r < 5; r++)
            for (c = 0; g[r][c]; c++)
                if (g[r][c] == 'o' && x + c < n * 8) px[x + c][r + 1] = 2;
        x += (int)strlen(g[0]) + 1;
    }
    for (t = 0; t < n; t++)
        for (r = 0; r < 8; r++) {
            unsigned lo = 0, hi = 0;
            for (c = 0; c < 8; c++) {
                lo |= (unsigned)(px[t * 8 + c][r] & 1) << (7 - c);
                hi |= (unsigned)(px[t * 8 + c][r] >> 1) << (7 - c);
            }
            out[t * 8 + r] = (uint16_t)(lo | hi << 8);
        }
}

typedef struct {
    const char *text;
    uint16_t buffer;     /* where the game keeps the first tile's word in the WRAM, and the word it has there */
    uint16_t word;
    int row, col;        /* the first cell in the quarter of the map */
    int n;               /* tiles of the label */
    int own;             /* tiles the game draws for it (the others are taken from `spare`) */
    uint16_t tile[5];    /* the tiles of the label, as the tilemap names them (the first `own` are the game's) */
    uint8_t attr;        /* high byte of the map words */
} Label;

static const Label labels[] = {
    { "OBJETOS",   0x1146, 0x246E, 5,  3, 4, 2, { 0x06E, 0x06F, 0x1F8, 0x1F9 }, 0x24 },
    { "ACCION",    0x1546, 0x2482, 21, 3, 3, 2, { 0x082, 0x083, 0x1FA }, 0x24 },
    { "COLGANTES", 0x132C, 0x2521, 12, 22, 5, 5, { 0x121, 0x122, 0x123, 0x124, 0x13F }, 0x25 },
    { "EQUIPO",    0x15AC, 0x2479, 22, 22, 5, 5, { 0x079, 0x07A, 0x07B, 0x07C, 0x08C }, 0x24 },
};

void alttp_pause_labels(void) {
    int n, t, r;
    uint16_t bitmaps[5 * 8];
    if (wram_read8(0x10) != 0x0E) return;
    for (n = 0; n < (int)(sizeof labels / sizeof labels[0]); n++) {
        const Label *lb = &labels[n];
        uint16_t w = (uint16_t)(wram_read8(lb->buffer) | wram_read8(lb->buffer + 1u) << 8);
        if (w != lb->word) continue; /* not the screen with the four boxes */
        if (ppu_vram_read16((uint16_t)(BG3_SHEET + (uint32_t)(lb->tile[0] & 0x1FF) * 8u)) != 0xFFFFu) continue; /* not the game's tile: the tiles' first row is all colour 3 */
        label_tiles(lb->text, lb->n, bitmaps);
        for (t = 0; t < lb->n; t++) {
            for (r = 0; r < 8; r++) ppu_vram_write16((uint16_t)(BG3_SHEET + (uint32_t)(lb->tile[t] & 0x1FF) * 8u + (uint32_t)r), bitmaps[t * 8 + r]);
            ppu_vram_write16((uint16_t)(BG3_MAP + (uint32_t)lb->row * 32u + (uint32_t)lb->col + (uint32_t)t), (uint16_t)(((lb->attr & 0xFE) | (lb->tile[t] >> 8)) << 8 | (lb->tile[t] & 0xFF)));
        }
    }
}
