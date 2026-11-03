// Explanations consume the audited exact model; plots alone convert to numbers.
import {analyzeRecovery, presetExperiment} from './recovery-lab-core.mjs';

export const LESSONS = [
  {title:'1. Lose information', preset:'sum', question:0,
    idea:'A summary groups inputs together. If it records only a total, it cannot tell you how that total was split.',
    example:'The inputs (1, 0) and (0, 1) both have total 1. Their first coordinates are 1 and 0.',
    task:'In the workspace, move t from 1 to −1. Watch the input move while the total stays fixed.',
    prompt:'Could any rule using only the total recover the first coordinate for every input?',
    choices:['Yes, with a clever enough rule','No, the same total can need different answers'], correct:1,
    explanation:'A rule would have to send the same total, 1, to both 1 and 0. A function gives one answer for each input, so this is impossible. This rules out nonlinear rules too.'},
  {title:'2. Recover an answer', preset:'sufficient', question:0,
    idea:'You can know the answer to a question while some of the original input remains hidden.',
    example:'Measure y₁ = x₁ + x₂ and y₂ = x₂ + x₃. Then 2y₁ + y₂ = 2x₁ + 3x₂ + x₃, the requested answer.',
    task:'Move t. The three input coordinates change, but both measurements and the requested answer stay fixed. Read the numerical substitution under the certificate.',
    prompt:'Must the measurements determine all three input coordinates to answer this question?',
    choices:['No, the requested combination is enough','Yes, every coordinate must be known'], correct:0,
    explanation:'The rule 2y₁ + y₂ works for every input. One invisible direction remains, but this particular question does not change along it.'},
  {title:'3. Compare questions', preset:'partial', question:1,
    idea:'Sufficiency depends on the question. The same measurements can answer one question and fail on another.',
    example:'Keep x₁ + x₂ and x₃. The question F₁ = 2x₁ + 2x₂ is twice the first measurement. The question F₂ = x₁ − x₂ can still change.',
    task:'Switch between F₁ and F₂ in “Test recovery”. Compare the flat and sloping answer graphs.',
    prompt:'With these measurements, which questions are recoverable?',
    choices:['Both questions','F₁ alone','Neither question'], correct:1,
    explanation:'F₁ = 2y₁. Along w = (1, −1, 0), both measurements stay fixed, while F₂ changes by 2 per step. Recovery is a separate test for each question.'},
  {title:'4. Repair the summary', preset:'partial', question:1,
    idea:'Repair keeps enough of the old information and adds a measurement that detects the missing question direction.',
    example:'Here, adding the measurement x₁ − x₂ is enough to answer both questions. Adding no measurement would leave F₂ obstructed, so one is the minimum.',
    task:'Select “Build a sufficient summary”, inspect the new recovery rules, then use Undo. Try the “More rows, no more information” starter next.',
    prompt:'Would adding a second copy of x₁ + x₂ repair the missing difference?',
    choices:['Yes, another row always helps','No, a repeated measurement adds no information'], correct:1,
    explanation:'A repeated total still erases (1, −1, 0). The extra row must add an independent direction. Rank counts independent information, so a row count alone cannot measure sufficiency.'}
];

export function lessonExperiment(index) {
  const lesson=LESSONS[index];
  if(!lesson) throw new RangeError('Unknown guided step.');
  return {...presetExperiment(lesson.preset), question:lesson.question};
}

export function linearExpression(coefficients, names) {
  const terms=[];
  coefficients.forEach((value,i)=>{
    if(value==='0') return;
    const negative=value.startsWith('-'), magnitude=negative?value.slice(1):value;
    const term=magnitude==='1'?names[i]:`${magnitude} × ${names[i]}`;
    terms.push((terms.length?(negative?' − ':' + '):(negative?'−':''))+term);
  });
  return terms.join('')||'0';
}

export function workedExplanation(result) {
  const {state,motion,questions,active}=result, q=questions[state.question];
  if(q.recoverable) {
    const enabledValues=new Map(active.map((index,j)=>[index,motion.summary[j]]));
    const values=state.R.map((_,i)=>`(${enabledValues.get(i)??'0'})`);
    return {title:'Use the measurements to calculate the answer',
      calculation:linearExpression(q.weights,values)+' = '+motion.answers[state.question],
      text:`At the base input x = (${motion.x.join(', ')}), the enabled measurements are (${motion.summary.join(', ')}). Substituting them in the recovery rule gives ${motion.answers[state.question]}. The coefficient identity above establishes that the rule works for every input.`};
  }
  const pair=analyzeRecovery({...state,t:1}).motion;
  return {title:'A proof pair: take one step along w',
    calculation:`x = (${pair.x.join(', ')}); x + w = (${pair.moved.join(', ')})`,
    text:`Both inputs give the enabled summary (${pair.summary.join(', ')}), but the selected answers are ${pair.answers[state.question]} and ${pair.movedAnswers[state.question]}. One summary would need two answers. This pair uses t = 1 even when the exploration slider is at zero.`};
}

export function motionSamples(state) {
  return Array.from({length:9},(_,i)=>{
    const t=i-4, result=analyzeRecovery({...state,t});
    return {t,summary:result.motion.movedSummary,answer:result.motion.movedAnswers[state.question]};
  });
}

export function asNumber(value) {
  const [n,d='1']=value.split('/');
  return Number(n)/Number(d);
}
