// Synchronous loop adapted from Lean/Elab/Frontend.lean in the pinned Lean fork.
// Copyright (c) 2019 Microsoft Corporation; Apache-2.0 (LICENSE-APACHE.txt).
// One synchronous frontend execution with parser diagnostics preserved before
// Lean's command elaborator clears its message log. This uses the pinned fork's
// exported-only imports; it does not claim native private-module equivalence.
// The caller must preload libraries, use a fresh worker for each Run, require
// the exact completion marker, and never retry source execution automatically.
import {leanSourceExpression, leanStringLiteral} from './syntax-probe.js?v=20261102-frontend1';

export function frontendMarkers(nonce) {
  if (typeof nonce !== 'string' || !/^[0-9a-f]{32}$/.test(nonce)) {
    throw new Error('Expected a fresh 128-bit hexadecimal nonce.');
  }
  return {
    started: '__KOMOREBI_FRONTEND_STARTED_' + nonce + '__',
    completed: '__KOMOREBI_FRONTEND_COMPLETED_' + nonce + '__',
    fileName: '<komorebi-frontend-' + nonce + '>'
  };
}

export function checkedFrontendSource(code, {mainModule = null, nonce} = {}) {
  if (typeof code !== 'string') throw new TypeError('Source must be a string.');
  // The shared literal builder normalizes these characters. Reject the ORIGINAL
  // input first so the frontend always checks precisely the supplied source.
  if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f\u2028\u2029]/.test(code)) {
    throw new Error('Source contains unsupported control characters.');
  }
  const markers = frontendMarkers(nonce);
  if (mainModule !== null && (typeof mainModule !== 'string' ||
      !/^[\p{ID_Start}_][\p{ID_Continue}']*(\.[\p{ID_Start}_][\p{ID_Continue}']*)*$/u.test(mainModule))) {
    throw new Error('Invalid main module.');
  }
  // Anonymous matches the fork's ordinary input environment. A dependency may
  // supply its real module name before mkState derives private auxiliary names.
  const values = {
    SOURCE_EXPRESSION_HERE: leanSourceExpression(code),
    MAIN_MODULE_HERE: mainModule === null ? 'Name.anonymous' : '`' + mainModule,
    INPUT_FILE_NAME_HERE: leanStringLiteral(markers.fileName),
    __STARTED_NONCE__: markers.started,
    __COMPLETED_NONCE__: markers.completed
  };
  // One callback pass: source text is not rescanned, and $&/$`/$' stay literal.
  return TEMPLATE.replace(/SOURCE_EXPRESSION_HERE|MAIN_MODULE_HERE|INPUT_FILE_NAME_HERE|__STARTED_NONCE__|__COMPLETED_NONCE__/g,
    token => values[token]);
}

const TEMPLATE = `module
import Lean
meta import Lean.Elab.Frontend
open Lean
run_cmd do
  let src := SOURCE_EXPRESSION_HERE
  let ictx := Parser.mkInputContext src INPUT_FILE_NAME_HERE
  let (header, ps, headerMessages) ← Parser.parseHeader ictx
  let opts : Options := Elab.async.set {} false
  -- Re-import the ORIGINAL exact header; outer Lean is transport, not an extra user import.
  -- Matches this fork's exported-only runtime. Do not use ordinary native private-level imports.
  unsafe enableInitializersExecution
  let importedEnv ← importModules (Elab.headerToImports header) opts 0
    (level := .exported) (loadExts := true) (leakEnv := true)
  let env := importedEnv.setMainModule MAIN_MODULE_HERE
  let commandState := Elab.Command.mkState env {} opts
  let frontendContext : Elab.Frontend.Context := { inputCtx := ictx }
  let frontendState : Elab.Frontend.State :=
    { commandState, parserState := ps, cmdPos := ps.pos }
  logInfo "__STARTED_NONCE__"
  let ensureSynchronous (state : Elab.Command.State) (phase : String) : IO Unit := do
    if state.scopes.any (fun scope => Elab.async.get scope.opts) then
      throw <| IO.userError ("Experimental frontend rejects asynchronous elaboration " ++ phase)
    if !state.snapshotTasks.isEmpty then
      throw <| IO.userError ("Experimental frontend rejects pending command tasks " ++ phase)
  let execute : Elab.Frontend.FrontendM MessageLog := do
    let mut messages : MessageLog := headerMessages
    let mut done := false
    while !done do
      Elab.Frontend.updateCmdPos
      let commandState ← Elab.Frontend.getCommandState
      ensureSynchronous commandState "before command"
      let parserState ← Elab.Frontend.getParserState
      let scope := commandState.scopes.head!
      let parserContext : Parser.ParserModuleContext :=
        { env := commandState.env, options := scope.opts,
          currNamespace := scope.currNamespace, openDecls := scope.openDecls }
      let (command, nextParserState, parseMessages) :=
        Parser.parseCommand ictx parserContext parserState {}
      if Parser.isTerminalCommand command && !command.isOfKind \`\`Parser.Command.eoi then
        throw <| IO.userError "Experimental frontend requires end of input; early terminal command rejected"
      if command.isOfKind \`\`Parser.Command.eoi && !ictx.atEnd nextParserState.pos then
        throw <| IO.userError "Experimental frontend requires actual end of input; premature eoi node rejected"
      -- Save parse errors BEFORE elabCommandTopLevel clears its own message log.
      messages := messages ++ parseMessages
      Elab.Frontend.setParserState nextParserState
      Elab.Frontend.setMessages parseMessages
      Elab.Frontend.elabCommandAtFrontend command
      let afterCommand ← Elab.Frontend.getCommandState
      ensureSynchronous afterCommand "after command"
      messages := messages ++ afterCommand.messages
      done := command.isOfKind \`\`Parser.Command.eoi
    return messages
  let execution : IO (MessageLog × Elab.Frontend.State) :=
    StateRefT'.run (ReaderT.run execute frontendContext) frontendState
  let (messages, _) ← execution
  modify fun s => { s with messages := s.messages ++ messages }
  logInfo "__COMPLETED_NONCE__"
`;
