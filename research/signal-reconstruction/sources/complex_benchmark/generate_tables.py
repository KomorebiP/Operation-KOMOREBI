from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generated_tables'
OUT.mkdir(exist_ok=True)

def esc(s):
    return str(s).replace('_','\\_').replace('%','\\%').replace('&','\\&')

def disp(s):
    return esc(str(s).replace('_',' '))

def fnum(x):
    try:
        x=float(x)
    except Exception:
        return esc(x)
    if not np.isfinite(x):
        return r'$\infty$'
    if x==0:
        return '0'
    if abs(x)>=1000 or abs(x)<1e-3:
        return f'${x:.3e}$'
    return f'{x:.4f}'

# 1D cases
D=pd.read_csv(ROOT/'tables/one_dimensional_cases.csv')
lines=[r'\begin{longtable}{p{0.22\linewidth}rrrrrr}',
       r'\caption{Complex one-dimensional benchmark cases.}\label{tab:one-d-cases}\\',
       r'\toprule',
       r'Case & $L$ & $\widehat L$ & location error & jump error & raw RMSE & resolved RMSE\\',
       r'\midrule\endfirsthead',
       r'\toprule Case & $L$ & $\widehat L$ & location error & jump error & raw RMSE & resolved RMSE\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{disp(r['case'])} & {int(r['true_order'])} & {int(r['recovered_order'])} & {fnum(r['location_error'])} & {fnum(r['jump_error'])} & {fnum(r['raw_rmse'])} & {fnum(r['resolved_rmse'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}']
(OUT/'one_d_cases.tex').write_text('\n'.join(lines))

# 1D noise
D=pd.read_csv(ROOT/'tables/one_dimensional_noise.csv')
lines=[r'{\scriptsize\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{rrrrrr}',r'\caption{Six-jump noise sweep.}\label{tab:one-d-noise}\\',r'\toprule',r'$\sigma$ & order accuracy & success & median location error & max location error & median jump error\\',r'\midrule\endfirsthead',r'\toprule $\sigma$ & order accuracy & success & median location error & max location error & median jump error\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{fnum(r['sigma'])} & {fnum(r['order_accuracy'])} & {fnum(r['success_rate'])} & {fnum(r['median_location_error'])} & {fnum(r['maximum_location_error'])} & {fnum(r['median_jump_error'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}']
lines.append(r'}')
(OUT/'one_d_noise.tex').write_text('\n'.join(lines))

# separation
D=pd.read_csv(ROOT/'tables/one_dimensional_separation.csv')
lines=[r'{\scriptsize\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{rrrrrr}',r'\caption{Near-collision sweep with fixed moment noise $\sigma=10^{-3}$.}\label{tab:separation}\\',r'\toprule',r'separation & location error & jump error & success & $\sigma_{\min}(V)$ & phase residual\\',r'\midrule\endfirsthead',r'\toprule separation & location error & jump error & success & $\sigma_{\min}(V)$ & phase residual\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{fnum(r['separation'])} & {fnum(r['location_error'])} & {fnum(r['jump_error'])} & {fnum(r['success'])} & {fnum(r['smallest_vandermonde_singular'])} & {fnum(r['phase_residual'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}']
lines.append(r'}')
(OUT/'separation.tex').write_text('\n'.join(lines))

# order
D=pd.read_csv(ROOT/'tables/one_dimensional_order.csv')
lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Model-order sweep.}\label{tab:order-sweep}',r'\begin{tabular}{rrrrr}\toprule',r'$L$ & cases & success & median location error & median runtime (s)\\\midrule']
for _,r in D.iterrows():
    lines.append(f"{int(r['order'])} & {int(r['cases'])} & {fnum(r['success_rate'])} & {fnum(r['median_location_error'])} & {fnum(r['median_runtime_seconds'])}\\\\")
lines += [r'\bottomrule\end{tabular}\end{table}']
(OUT/'order_sweep.tex').write_text('\n'.join(lines))

# 2D exact all metrics
D=pd.read_csv(ROOT/'tables/two_dimensional_exact.csv')
lines=[r'{\scriptsize\setlength{\tabcolsep}{2.5pt}',r'\begin{longtable}{p{0.15\linewidth}p{0.15\linewidth}rrrrrr}',r'\caption{Exact-dictionary two-dimensional benchmark.}\label{tab:two-d-exact}\\',r'\toprule',r'Case & Method & RMSE & PSNR & SSIM & boundary RMSE & edge IoU & selected\\',r'\midrule\endfirsthead',r'\toprule Case & Method & RMSE & PSNR & SSIM & boundary RMSE & edge IoU & selected\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{disp(r['case'])} & {disp(r['method'])} & {fnum(r['rmse'])} & {fnum(r['psnr'])} & {fnum(r['ssim'])} & {fnum(r['boundary_rmse'])} & {fnum(r['edge_iou'])} & {int(r['selected_atoms'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}']
lines.append(r'}')
(OUT/'two_d_exact.tex').write_text('\n'.join(lines))

# 2D noise
D=pd.read_csv(ROOT/'tables/two_dimensional_noise.csv')
lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Noise sweep for the four-atom geometric image.}\label{tab:two-d-noise}',r'\begin{tabular}{rrrr}\toprule',r'$\sigma$ & median RMSE & median support IoU & median selected count\\\midrule']
for _,r in D.iterrows():
    lines.append(f"{fnum(r['sigma'])} & {fnum(r['median_rmse'])} & {fnum(r['median_support_iou'])} & {fnum(r['median_selected_count'])}\\\\")
lines += [r'\bottomrule\end{tabular}\end{table}']
(OUT/'two_d_noise.tex').write_text('\n'.join(lines))

# random summary
D=pd.read_csv(ROOT/'tables/two_dimensional_random.csv')
summary={
    'cases':len(D),
    'support_iou_median':D.support_iou.median(),
    'support_iou_min':D.support_iou.min(),
    'count_accuracy':np.mean(D.true_count==D.selected_count),
    'raw_rmse_median':D.raw_rmse.median(),
    'resolved_rmse_median':D.resolved_rmse.median(),
    'ratio':D.resolved_rmse.median()/D.raw_rmse.median(),
}
lines=[r'\begin{table}[htbp]\centering',r'\caption{Summary of forty random finite-dictionary image cases.}\label{tab:two-d-random}',r'\begin{tabular}{lr}\toprule',r'Quantity & Value\\\midrule']
for k,v in summary.items():
    label=k.replace('_',' ')
    lines.append(f"{esc(label)} & {fnum(v)}\\\\")
lines += [r'\bottomrule\end{tabular}\end{table}']
(OUT/'two_d_random_summary.tex').write_text('\n'.join(lines))

# out of model
D=pd.read_csv(ROOT/'tables/out_of_model_images.csv')
lines=[r'{\scriptsize\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{p{0.18\linewidth}p{0.17\linewidth}rrrr}',r'\caption{Out-of-dictionary image results.}\label{tab:out-model}\\',r'\toprule',r'Case & Method & RMSE & SSIM & boundary RMSE & edge IoU\\',r'\midrule\endfirsthead',r'\toprule Case & Method & RMSE & SSIM & boundary RMSE & edge IoU\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{disp(r['case'])} & {disp(r['method'])} & {fnum(r['rmse'])} & {fnum(r['ssim'])} & {fnum(r['boundary_rmse'])} & {fnum(r['edge_iou'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}']
lines.append(r'}')
(OUT/'out_model.tex').write_text('\n'.join(lines))

# natural
D=pd.read_csv(ROOT/'tables/natural_images.csv')
lines=[r'{\scriptsize\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{p{0.12\linewidth}p{0.18\linewidth}rrrr}',r'\caption{Exploratory natural-image results.}\label{tab:natural}\\',r'\toprule',r'Image & Method & RMSE & PSNR & SSIM & boundary RMSE\\',r'\midrule\endfirsthead',r'\toprule Image & Method & RMSE & PSNR & SSIM & boundary RMSE\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{disp(r['case'])} & {disp(r['method'])} & {fnum(r['rmse'])} & {fnum(r['psnr'])} & {fnum(r['ssim'])} & {fnum(r['boundary_rmse'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}']
lines.append(r'}')
(OUT/'natural.tex').write_text('\n'.join(lines))

# checks
D=pd.read_csv(ROOT/'tables/checks.csv')
lines=[r'\begin{longtable}{p{0.55\linewidth}p{0.10\linewidth}p{0.25\linewidth}}',r'\caption{Automated benchmark checks.}\label{tab:checks}\\',r'\toprule',r'Check & Passed & Detail\\',r'\midrule\endfirsthead',r'\toprule Check & Passed & Detail\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{esc(r['check'])} & {esc(r['passed'])} & {esc(r['detail'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}']
(OUT/'checks.tex').write_text('\n'.join(lines))


# full random rows
D=pd.read_csv(ROOT/'tables/two_dimensional_random.csv')
lines=[r'{\scriptsize\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{rrrrrr}',r'\caption{All forty random finite-dictionary image cases.}\label{tab:random-full}\\',r'\toprule',r'case & true count & selected count & support IoU & raw RMSE & resolved RMSE\\',r'\midrule\endfirsthead',r'\toprule case & true count & selected count & support IoU & raw RMSE & resolved RMSE\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{int(r['case'])} & {int(r['true_count'])} & {int(r['selected_count'])} & {fnum(r['support_iou'])} & {fnum(r['raw_rmse'])} & {fnum(r['resolved_rmse'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}',r'}']
(OUT/'two_d_random_full.tex').write_text('\n'.join(lines))

# natural hybrid
D=pd.read_csv(ROOT/'tables/natural_hybrid.csv')
lines=[r'{\scriptsize\setlength{\tabcolsep}{3pt}',r'\begin{longtable}{p{0.18\linewidth}rrrrrr}',r'\caption{Natural-background hybrid metrics.}\label{tab:hybrid}\\',r'\toprule',r'Method & RMSE & PSNR & SSIM & boundary RMSE & edge IoU & selected\\',r'\midrule\endfirsthead',r'\toprule Method & RMSE & PSNR & SSIM & boundary RMSE & edge IoU & selected\\\midrule\endhead']
for _,r in D.iterrows():
    lines.append(f"{disp(r['method'])} & {fnum(r['rmse'])} & {fnum(r['psnr'])} & {fnum(r['ssim'])} & {fnum(r['boundary_rmse'])} & {fnum(r['edge_iou'])} & {int(r['selected_atoms'])}\\\\")
lines += [r'\bottomrule',r'\end{longtable}',r'}']
(OUT/'hybrid.tex').write_text('\n'.join(lines))

print('generated',len(list(OUT.glob('*.tex'))),'tables')
