# New-chat Overleaf continuation prompt

The old chat has a confirmed stored conflict: global Overleaf permission is allowed but that conversation has an explicit Overleaf denial. No permission files were changed. Use this prompt in a genuinely new chat attached to the same Windows workspace, with the connected Chrome profile. The new chat must pass its own supported site-access check.

Suggested prompt to paste:

> @Chrome 请继续本机 MMME3086 CFD coursework 的 Overleaf 上传、编译与最终排版验收。先只读检查已登录的项目 https://www.overleaf.com/project/6aed174c208587f797ee667b 。如果权限检查通过，我授权读取、编辑、上传当前课程报告文件并编译这个现有项目；不要向 AIAA 或学校提交。若仍被站点策略拒绝，停止浏览器操作并报告，不绕过权限。
>
> 工作目录是 C:\Users\A320N\Documents\ChatGPT\MMME3086 cw1 。先读取 coordination/project_state.json、coordination/DELIVERY_README.md、report/source_package_status.json 和 review/final_report_content_review.md；使用最新已审查源码包及 asset_manifest，不采用历史案例或旧源码。
>
> 五个正式 CFD 案例、初始增强 RSM 诊断、网格与入口长度尺度补充计算均已完成；不要重新计算或改 Fluent。学号20617209，入口50.9m/s，全部物性须保留实际保存值。保留批准的 AIAA class、四个规定section与十三图顺序，遵守字数和八页要求；只能在 Overleaf 编译。正文无 TODO/working draft，展示公式末尾无标点。Case2/3的严格连续性目标未达标限制，以及Case5新增/global迭代区别必须保留。
>
> 下载实际编译PDF后逐页检查：页数、表格与图注、图轴和图例字号、缺字/裁切/溢出、跨页段落、公式、参考文献和AI记录。必要修改须重新在Overleaf编译并复核；在此之前不得宣称最终PDF验收通过。原始文件留存，工作成果保存至 D:\iCloud\iCloudDrive\iCloudDrive\Documents\Codex\MMME3086 cw1 (Windows)。

If the new read-only test also fails, update the supported desktop app/extension and submit a sanitized /feedback reproduction. Similar public reports are linked in `overleaf_permission_reproduction.md`. An observed conversation-level denial is not permission to rewrite internal authorization storage.
