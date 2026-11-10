# Optional nickname registration

Project: **ezygame**, from the supplied Netlify dashboard URL. This update adds
one optional form, `ezyplay-guest-registration`, to the existing Food Fight
Anonymous Mode screen. It does not add an account system or change Racer,
gameplay, currency, shops, controls, puzzle levels or save keys. Food Fight still
has the existing 12 puzzle levels; this update does not claim a 100-level expansion.

## Player flow

- **Play without registering** sends no registration, even if a nickname was
  typed. No consent is required to play.
- Registering requires a 3–24 character nickname (letters, numbers, underscores)
  and an explicitly checked consent box. No first/last name, email, password,
  device identifier or game progress is included.
- The POST body contains only `form-name`, `nickname`, `consent=yes` and the empty
  spam honeypot `bot-field`. It uses URL-encoded data and no cookies or referrer.
- The real static form has `method="POST"`, `data-netlify="true"`, a named
  honeypot and literal named inputs in `dist/Food_Fight_Development.html`.
  Netlify can detect it at build time even though its game screen starts hidden.
- While submitting, repeated taps are blocked. Requests time out after eight
  seconds. HTTP/network/timeout errors explain uncertain delivery and leave
  unregistered play available. There are no automatic retries. Only one attempt
  is allowed per guest session, including after a failure, to avoid an ambiguous
  failed response causing a duplicate. Reload/End Session begins another session;
  there is no cross-session or cross-device deduplication.
- A submitted nickname is displayed only for the current tab's session. It is
  never added to localStorage or game saves. No private submissions are fetched
  by public JavaScript. Anonymous play remains usable with storage blocked.

## Enable and verify on Netlify

1. Open <https://app.netlify.com/projects/ezygame/forms> while signed in.
2. If form detection is disabled, select **Enable form detection**. Depending on
   Netlify's current interface, this control may be under the Forms settings.
3. Review and merge/deploy the feature branch. The existing `netlify.toml`
   remains unchanged: build `node scripts/build.mjs`, publish `dist`. A **new
   deploy after enabling detection** is required for Netlify to scan the HTML.
4. Confirm **ezyplay-guest-registration** appears in Forms. If absent, check the
   deploy succeeded, detection is enabled, and the published HTML contains the
   named static form. This form uses Netlify hosting; a local Python server or
   Cloudflare Pages does not accept these submissions.
5. Open the deployed site's `/food-fight/`, select **Play Anonymously**, enter a
   test nickname and check consent. Submit once. In **Forms →
   ezyplay-guest-registration**, confirm the nickname and consent entry; check
   spam submissions if it is missing. Delete the test entry afterwards.
6. Try **Play without registering** and verify gameplay works with no new entry.
   Test offline submission and recovery to play. On iPad Safari, also check
   keyboard entry, checkbox taps, menu scrolling, touch aiming and rotation.

The supplied `/deploys/6af2d532b08affec4f5d746b` URL identifies the project;
it does not prove this code has been deployed or that detection is enabled.
No Netlify project settings or production deployment were changed by this work.

## Administrator access and retention

The existing local admin panel has a navigation link to that project's signed-in
Forms dashboard. The client-side password is **not secure authentication**.
Netlify's account permissions protect stored submissions. Displaying them inside
EzyPlay would require an authenticated server-side API with authorization;
no API, client credentials or public submission list has been added.

The public privacy notice describes voluntary sharing with the EzyPlay
administrator, Netlify's normal connection processing, and local game saves.
No removal contact address was supplied, so none is invented. Players may use
their existing administrator contact channel quoting just the nickname, or
choose unregistered play. Add a genuine public contact link before broadly
inviting registrations if no such channel exists.

**Operator task:** review entries weekly and manually delete them within **30
days**, or sooner when no longer needed or removal is requested. Include spam,
exports and notification copies. The static site cannot enforce server-side
retention or automatic deletion. Do not enable unnecessary notification copies.

## Verification

Build and serve `dist` using the README commands, then run:

```sh
FOODFIGHT_BASE_URL=http://127.0.0.1:8051 python3 tests/netlify_forms_checks.py
FOODFIGHT_BASE_URL=http://127.0.0.1:8051 python3 tests/guest_checks.py
```

Python Playwright and Chromium are test tools only, not website dependencies.
The new suite checks the built static form, unchecked consent, exact submission
fields, duplicate guards, successful response, failed HTTP/offline/timeout paths,
admin visibility/link, privacy, gameplay entry and unchanged raw save records
at desktop/tablet/phone sizes. POST responses are intercepted locally: this
verifies the client contract, **not actual Netlify receipt**. That needs the
deployed-site test above. Physical iPad/Safari testing remains necessary.

The existing game regression suites also run with registration skipped, ensuring
tests never submit real player data. The EzyPlay suite compares the complete
Food Fight gameplay/shop/save/input-handler block to audited commit b20444e;
the Forms suite compares every Racer file to that same baseline. Neither new
initialization nor guest navigation writes or deletes existing saved progress.

Results on November 10, 2026: the static build, JavaScript/Python syntax and
whitespace checks passed. All 12 suites passed: the four Racer Node suites,
six Food Fight browser suites, EzyPlay browser integration and the new Forms
suite. Browser tests used system Chromium at desktop, iPad-sized portrait and
landscape, and phone viewports. All 12 Racer tracks completed their recorded
actual-physics input replays; no gameplay/save regression or uncaught JavaScript
error was found. The final built form/privacy files match their source files.
This does not replace the outstanding physical iPad/Safari and live Netlify
receipt checks above.
