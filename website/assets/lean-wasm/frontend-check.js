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
    FRONTEND_NAMESPACE_HERE: 'KomorebiFrontend_' + nonce,
    SOURCE_EXPRESSION_HERE: leanSourceExpression(code),
    MAIN_MODULE_HERE: mainModule === null ? 'Name.anonymous' : '`' + mainModule,
    INPUT_FILE_NAME_HERE: leanStringLiteral(markers.fileName),
    __STARTED_NONCE__: markers.started,
    __COMPLETED_NONCE__: markers.completed
  };
  // One callback pass: source text is not rescanned, and $&/$`/$' stay literal.
  return TEMPLATE.replace(/FRONTEND_NAMESPACE_HERE|SOURCE_EXPRESSION_HERE|MAIN_MODULE_HERE|INPUT_FILE_NAME_HERE|__STARTED_NONCE__|__COMPLETED_NONCE__/g,
    token => values[token]);
}

const TEMPLATE = `module
import Lean
meta import Lean.Elab.Frontend
open Lean
-- Keep executable definitions separate: a larger nested run_cmd exceeded the
-- browser Wasm stack during elaboration even when its input source was trivial.
-- The transport executes the supplied source exactly once.

-- Shell output includes unreported messages only. A snapshot may hold already
-- reported errors, so preserve both halves as visible diagnostics.
meta def FRONTEND_NAMESPACE_HERE.normalizeMessages (log : MessageLog) : MessageLog :=
  { log with reported := {}, unreported := log.reportedPlusUnreported }

-- get is used only after hasFinished, which guarantees immediate return.
-- Cancellation and fatal state remain failures even for completed tasks.
meta def FRONTEND_NAMESPACE_HERE.readCompletedSnapshot
    (task : Language.SnapshotTask Language.SnapshotTree) : IO Language.SnapshotTree := do
  match task.cancelTk? with
  | some token =>
    if (← token.isSet) then
      throw (IO.userError "Experimental frontend rejects cancelled command tasks")
  | none => pure ()
  if !(← IO.hasFinished task.task) then
    throw (IO.userError "Experimental frontend rejects unfinished command tasks")
  let tree : Language.SnapshotTree := Language.SnapshotTask.get task
  if tree.element.isFatal then
    throw (IO.userError "Experimental frontend rejects fatal command snapshots")
  return tree

-- The second argument is the exact length of the pending list. Checking it
-- before appending children bounds both total visits and the live frontier.
meta def FRONTEND_NAMESPACE_HERE.collectCompletedSnapshots : Nat → Nat →
    List (Language.SnapshotTask Language.SnapshotTree) → MessageLog → IO MessageLog
  | _, _, [], messages => pure messages
  | 0, _, _ :: _, _ =>
    throw (IO.userError "Experimental frontend snapshot tree exceeds the completion bound")
  | fuel + 1, pendingCount, task :: rest, messages => do
    let tree ← FRONTEND_NAMESPACE_HERE.readCompletedSnapshot task
    let nextCount := pendingCount - 1 + tree.children.size
    if nextCount > fuel then
      throw (IO.userError "Experimental frontend snapshot tree exceeds the completion bound")
    let current := FRONTEND_NAMESPACE_HERE.normalizeMessages tree.element.diagnostics.msgLog
    FRONTEND_NAMESPACE_HERE.collectCompletedSnapshots fuel nextCount (tree.children.toList ++ rest) (messages ++ current)

-- The checked environment must be ready and use kernel trust level zero.
-- A command is cleared only after every reachable snapshot was validated.
meta def FRONTEND_NAMESPACE_HERE.finishCommand (state : Elab.Command.State) :
    IO (Elab.Command.State × MessageLog) := do
  if !(← IO.hasFinished state.env.checked) then
    throw (IO.userError "Experimental frontend rejects unfinished kernel checking")
  let checked : Kernel.Environment := Task.get state.env.checked
  if checked.header.trustLevel != 0 then
    throw (IO.userError "Experimental frontend requires kernel trust level zero")
  if state.snapshotTasks.size > 10000 then
    throw (IO.userError "Experimental frontend snapshot tree exceeds the completion bound")
  let messages ← FRONTEND_NAMESPACE_HERE.collectCompletedSnapshots 10000 state.snapshotTasks.size state.snapshotTasks.toList
    (FRONTEND_NAMESPACE_HERE.normalizeMessages state.messages)
  return ({state with snapshotTasks := #[]}, messages)


-- Explicit async scopes are unsupported; the previous command must already
-- have consumed its complete snapshot tree before parsing the next command.
meta def FRONTEND_NAMESPACE_HERE.checkBeforeCommand (state : Elab.Command.State) (phase : String) : IO Unit := do
  if state.scopes.any (fun scope => Elab.async.get scope.opts) then
    throw <| IO.userError ("Experimental frontend rejects asynchronous elaboration " ++ phase)
  if !state.snapshotTasks.isEmpty then
    throw <| IO.userError ("Experimental frontend rejects pending command tasks " ++ phase)

-- Check parsed literal opt-ins before execution, including temporary command,
-- term, and tactic scopes. Quoted syntax is data and is not executed here.
meta def FRONTEND_NAMESPACE_HERE.hasAsyncOptIn (command : Syntax) : Bool :=
  (command.findStack?
    (fun stx => !stx.isQuot && !stx.isOfKind \`\`Parser.Tactic.quotSeq)
    (fun stx =>
      (stx.isOfKind \`\`Parser.Command.«set_option» ||
       stx.isOfKind \`\`Parser.Term.«set_option» ||
       stx.isOfKind \`\`Parser.Tactic.«set_option») &&
      stx[1].getId.eraseMacroScopes == \`Elab.async &&
      stx[3].getAtomVal == "true")).isSome


meta def FRONTEND_NAMESPACE_HERE.execute (ictx : Parser.InputContext)
    (headerMessages : MessageLog) : Elab.Frontend.FrontendM MessageLog := do
  let mut messages := FRONTEND_NAMESPACE_HERE.normalizeMessages headerMessages
  let mut done := false
  while !done do
    Elab.Frontend.updateCmdPos
    let commandState ← Elab.Frontend.getCommandState
    FRONTEND_NAMESPACE_HERE.checkBeforeCommand commandState "before command"
    let parserState ← Elab.Frontend.getParserState
    let scope := commandState.scopes.head!
    let parserContext : Parser.ParserModuleContext :=
      { env := commandState.env, options := scope.opts,
        currNamespace := scope.currNamespace, openDecls := scope.openDecls }
    let (command, nextParserState, parseMessages) :=
      Parser.parseCommand ictx parserContext parserState {}
    if FRONTEND_NAMESPACE_HERE.hasAsyncOptIn command then
      throw <| IO.userError "Experimental frontend rejects explicit asynchronous elaboration options"
    if Parser.isTerminalCommand command && !command.isOfKind \`\`Parser.Command.eoi then
      throw <| IO.userError "Experimental frontend requires end of input; early terminal command rejected"
    if command.isOfKind \`\`Parser.Command.eoi && !ictx.atEnd nextParserState.pos then
      throw <| IO.userError "Experimental frontend requires actual end of input; premature eoi node rejected"
    -- Save parse errors BEFORE elabCommandTopLevel clears its own message log.
    messages := messages ++ FRONTEND_NAMESPACE_HERE.normalizeMessages parseMessages
    Elab.Frontend.setParserState nextParserState
    Elab.Frontend.setMessages parseMessages
    Elab.Frontend.elabCommandAtFrontend command
    let afterCommand ← Elab.Frontend.getCommandState
    if afterCommand.scopes.any (fun scope => Elab.async.get scope.opts) then
      throw <| IO.userError "Experimental frontend rejects asynchronous elaboration after command"
    let (completedState, commandMessages) ← FRONTEND_NAMESPACE_HERE.finishCommand afterCommand
    Elab.Frontend.setCommandState completedState
    messages := messages ++ commandMessages
    done := command.isOfKind \`\`Parser.Command.eoi
  return messages

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
  -- Import initializers can grow the global extension registry. The outer
  -- command must use the updated environment before logging or running linters.
  setEnv env
  let commandState := Elab.Command.mkState env {} opts
  let frontendContext : Elab.Frontend.Context := { inputCtx := ictx }
  let frontendState : Elab.Frontend.State :=
    { commandState, parserState := ps, cmdPos := ps.pos }
  logInfo "__STARTED_NONCE__"
  let execution : IO (MessageLog × Elab.Frontend.State) :=
    StateRefT'.run (ReaderT.run (FRONTEND_NAMESPACE_HERE.execute ictx headerMessages) frontendContext) frontendState
  let (messages, finalState) ← execution
  -- Outer command linters still run after this action. Carry its final
  -- environment forward without replacing the outer scopes or file context.
  setEnv finalState.commandState.env
  modify fun s => { s with messages := s.messages ++ messages }
  logInfo "__COMPLETED_NONCE__"
`;
