<?php
/**
 * raimes.ai page-view counter (added 2026-10-18).
 *
 * One number per day, nothing else. The page sends one POST per view (navigator.sendBeacon in
 * layouts/_partials/extend_footer.html); this script adds 1 to today's count in a JSON file that lives
 * in the account's home directory, outside the web root, so the deploy (lftp mirror --delete) never
 * touches it. No cookie, no IP address, no referrer, no user agent and no timestamp are stored.
 *
 *   POST /stats/hit.php          count one page view, answer 204
 *   GET  /stats/today.json       today's count as JSON (rewritten to hit.php?json=1 in static/.htaccess)
 *
 * Bots are filtered coarsely by user agent; most do not run JavaScript anyway. Requests must come
 * from the site itself (Origin / Sec-Fetch-Site when the browser sends them). PHP 8.2 on Hetzner.
 */
declare(strict_types=1);

const DATA_DIR  = 'raimes-counter';   // under $HOME (/usr/home/<account>/), created on first hit
const KEEP_DAYS = 400;                // daily counts kept; older keys are dropped on write
const SITE      = 'https://raimes.ai';
const BOT_UA    = '~bot|crawl|spider|slurp|fetch|curl|wget|python|java/|go-http|httpclient|headless|'
                . 'lighthouse|pagespeed|preview|monitor|scanner|check|uptime|facebookexternalhit|'
                . 'whatsapp|telegram|discord|slack|skype|embedly|quora|pinterest|yandex|baidu|'
                . 'semrush|ahrefs|mj12|dotbot|petal|bytespider|gptbot|claudebot|anthropic|openai|'
                . 'perplexity|ccbot|applebot|duckduck|bingpreview|ia_archiver~i';

date_default_timezone_set('Europe/Berlin');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

$home = getenv('HOME') ?: ($_SERVER['HOME'] ?? '');
if ($home === '' && function_exists('posix_getpwuid')) {
    $home = posix_getpwuid(posix_geteuid())['dir'] ?? '';
}
if ($home === '') {
    http_response_code(500);
    exit;
}
$dir   = rtrim($home, '/') . '/' . DATA_DIR;
$file  = $dir . '/counts.json';
$today = date('Y-m-d');

if (isset($_GET['json'])) {
    $counts = [];
    $mtime  = null;
    if (is_file($file) && ($fh = fopen($file, 'r')) !== false) {
        if (flock($fh, LOCK_SH)) {
            $counts = json_decode((string) stream_get_contents($fh), true) ?: [];
            flock($fh, LOCK_UN);
        }
        fclose($fh);
        $mtime = filemtime($file) ?: null;
    }
    krsort($counts);
    $yesterday = date('Y-m-d', strtotime('-1 day'));
    $out = [
        'date'      => $today,
        'today'     => (int) ($counts[$today] ?? 0),
        'yesterday' => (int) ($counts[$yesterday] ?? 0),
        'days'      => (object) array_slice($counts, 0, 14, true),
        'updated'   => $mtime ? date('c', $mtime) : null,
        'generated' => date('c'),
    ];
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($out, JSON_UNESCAPED_SLASHES), "\n";
    exit;
}

// Everything below counts a view and never returns a body.
http_response_code(204);

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    exit;   // GET on hit.php (link checkers, curious readers) counts nothing
}
$ua = $_SERVER['HTTP_USER_AGENT'] ?? '';
if ($ua === '' || preg_match(BOT_UA, $ua)) {
    exit;
}
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if ($origin !== '' && $origin !== SITE) {
    exit;
}
$site = $_SERVER['HTTP_SEC_FETCH_SITE'] ?? '';
if ($site !== '' && $site !== 'same-origin') {
    exit;
}

if (!is_dir($dir) && !@mkdir($dir, 0700, true)) {
    exit;
}
$fh = fopen($file, 'c+');
if ($fh === false || !flock($fh, LOCK_EX)) {
    exit;
}
$counts = json_decode((string) stream_get_contents($fh), true);
if (!is_array($counts)) {
    $counts = [];
}
$counts[$today] = (int) ($counts[$today] ?? 0) + 1;
ksort($counts);
$cutoff = date('Y-m-d', strtotime('-' . KEEP_DAYS . ' days'));
foreach (array_keys($counts) as $day) {
    if ($day < $cutoff) {
        unset($counts[$day]);
    }
}
rewind($fh);
ftruncate($fh, 0);
fwrite($fh, json_encode($counts, JSON_PRETTY_PRINT) . "\n");
fflush($fh);
flock($fh, LOCK_UN);
fclose($fh);
