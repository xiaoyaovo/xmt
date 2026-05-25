# Frontend Type Safety

The frontend is currently JavaScript-first, not TypeScript-first. Type safety comes from runtime prop validation, normalized API helpers, explicit data shaping, and generated auto-import declarations.

## Current Type Surface

- Vue SFCs use JavaScript in `<script setup>`.
- Props use runtime validators through `defineProps()`.
- API helpers return unwrapped response data from Axios.
- `src/auto-imports.d.ts` is generated for auto imports and should not be hand-authored as a source of application types.

## Runtime Validation

Validate at boundaries:

- Component props should declare `type`, `required`, and defaults.
- Backend response handling should tolerate missing fields when the UI can recover.
- CSV parsing normalizes headers and row lengths in `useCsvPreview.js`.
- Auth callback/token handling validates through `/auth/me` after storing the token.

## Data Shapes

Keep data shape conversions close to the boundary:

- Backend serializes ORM models through `serialize_*` functions and Pydantic schemas.
- Frontend API helpers should not return Axios response envelopes.
- Composables should expose stable field names that match what pages render.

When using backend field names in frontend code, match the API schema (`row_count`, `original_filename`, `item_key`) rather than inventing camelCase aliases unless a deliberate normalization layer is added.

## Nullability

Use explicit null/empty states:

- `activeFile = shallowRef(null)`
- `activeItem = shallowRef(null)`
- empty arrays for list state
- `errorMessage = shallowRef('')`

Templates should guard optional values before rendering nested fields.

## Generated Types

Do not manually edit generated declarations such as `frontend/src/auto-imports.d.ts`. If auto-import behavior changes, update `frontend/quasar.config.js` and regenerate.

## Avoid

- Using TypeScript syntax in `.js` files.
- Relying on backend data fields without null guards when the user may be logged out or a request may fail.
- Adding ad hoc frontend type aliases in comments. If the project moves to TypeScript later, create real `.ts` types in a planned migration.
