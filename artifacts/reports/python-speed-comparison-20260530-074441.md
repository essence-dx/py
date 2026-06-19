# Python Speed Comparison

Created: 2026-05-30T07:44:41.0199649+06:00

## Builds

- Official: G:\Dx\python\artifacts\official\3.14.5\pythoncore-amd64\runtime\python.exe
- Official version: Python 3.14.5 (tags/v3.14.5:5607950, May 10 2026, 10:43:50) [MSC v.1944 64 bit (AMD64)]
- Local: G:\Dx\python\cpython\PCbuild\amd64\python.exe
- Local version: Python 3.16.0a0 (heads/dev-dirty:5535c1f9c08, May 30 2026, 07:34:13) [MSC v.1950 64 bit (AMD64)]
- Local SHA256: EA58FF2DBF9C3166D61BA9C795824030CACDFA1735DE612708929FFEBE1D2AB9

## Fresh Logs

- Build: G:\Dx\python\artifacts\logs\local-build-release-x64-experimental-jit-off-rebuild-20260530-072930.log
- Smoke default: G:\Dx\python\artifacts\logs\jit-rebuild-smoke-test-sys-default-20260530-074012.log
- Smoke jit: G:\Dx\python\artifacts\logs\jit-rebuild-smoke-test-sys-jit-20260530-074012.log
- Smoke native-jit: G:\Dx\python\artifacts\logs\jit-rebuild-smoke-test-sys-native-jit-20260530-074012.log
- Benchmark: G:\Dx\python\artifacts\logs\jit-rebuild-speed-compare-20260530-074051.log
- Benchmark summary: G:\Dx\python\benchmarks\runs\20260530-074052\summary.csv
- JIT code range probe: G:\Dx\python\artifacts\logs\jit-code-range-probe-20260530-074335.log

## Benchmark Summary CSV

```csv
scenario,metric,median_seconds,min_seconds,pct_slower_vs_official_default_median
official-default,startup,0.068327700,0.045424400,0.000
official-jit,startup,0.049038300,0.035070600,-28.231
local-default,startup,0.118754550,0.069985400,73.801
local-jit,startup,0.053467350,0.042887300,-21.749
local-native-jit,startup,0.047082850,0.037941700,-31.093
official-default,int_loop,0.209520100,0.169738900,0.000
official-jit,int_loop,0.283035500,0.200999500,35.088
local-default,int_loop,0.571655000,0.493743500,172.840
local-jit,int_loop,0.327661300,0.299726200,56.387
local-native-jit,int_loop,0.330186600,0.305128800,57.592
official-default,function_calls,0.340240800,0.269650500,0.000
official-jit,function_calls,0.369553400,0.335734600,8.615
local-default,function_calls,0.800711100,0.739750700,135.337
local-jit,function_calls,0.404488500,0.319598000,18.883
local-native-jit,function_calls,0.518487500,0.406383300,52.388
official-default,list_dict,0.073943500,0.059683200,0.000
official-jit,list_dict,0.096620600,0.082091800,30.668
local-default,list_dict,0.095795000,0.080148800,29.552
local-jit,list_dict,0.070349000,0.050550000,-4.861
local-native-jit,list_dict,0.082623100,0.079919400,11.738
official-default,json_regex,0.027123400,0.023858600,0.000
official-jit,json_regex,0.043201900,0.036416700,59.279
local-default,json_regex,0.032521700,0.030422500,19.903
local-jit,json_regex,0.035200600,0.028179700,29.779
local-native-jit,json_regex,0.050207700,0.042142300,85.108
official-default,decimal_math,0.093566800,0.090447900,0.000
official-jit,decimal_math,0.211937300,0.162866800,126.509
local-default,decimal_math,0.112070300,0.103648200,19.776
local-jit,decimal_math,0.118118300,0.087026300,26.240
local-native-jit,decimal_math,0.215628900,0.187177400,130.454
official-default,class_attr,0.179437000,0.159475600,0.000
official-jit,class_attr,0.207216000,0.160117400,15.481
local-default,class_attr,0.466394700,0.378698100,159.921
local-jit,class_attr,0.199384900,0.177731100,11.117
local-native-jit,class_attr,0.170288400,0.155924300,-5.099
```

## Brutal Result

Official Python 3.14.5 default is the best broad winner in this fresh run. Local native-JIT only wins class_attr and startup; it loses int_loop, function_calls, json_regex, and decimal_math. The code-range probe shows local-jit and local-native-jit produce the same range counts/sizes for these workloads, so the current native path is not yet turning hot benchmark loops into better native machine code.
