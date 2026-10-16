import os
from threading import Lock

from PIL import Image

from jmcomic import *
from jmcomic.cli import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
145252

145260

145270

145275

145285

145286

145298

145327

145328

145329

145360

145379

145381

145388

145391

145397

145398

145414

145418

145426

145439

145441

145443

145453

145462

145468

145470

145478

145480

145484

145505

145507

145508

145509

145510

145512

145525

145526

145529

145532

145538

145545

145546

145547

145569

145581

145582

145597

145602

145613

145624

145628

145629

145646

145649

145652

145676

145679

145682

145687

145696

145712

145718

145732

145738

145749

145758

145775

145797

145831

145832

145834

145841

145844

145856

145857

145872

145876

145879

145880

145884

145889

145920

145921

145924

145934

145935

145936

145951

145956

145967

145992

146003

146010

146012

146017

146044

146047

146060

146064

146074

146098

146099

146109

146126

146132

146147

146148

146149

146150

146152

146154

146156

146159

146165

146167

146168

146194

146195

146197

146198

146199

146200

146201

146202

146212

146213

146215

146216

146222

146224

146225

146226

146228

146229

146231

146241

146255

146257

146261

146262

146263

146272

146276

146286

146289

146294

146298

146299

146300

146301

146311

146319

146320

146322

146325

146326

146327

146334

146335

146342

146348

146349

146350

146351

146352

146353

146354

146355

146359

146360

146361

146362

146368

146369

146370

146384

146385

146389

146394

146407

146414

146419

146421

146422

146424

146425

146427

146429

146430

146432

146435

146436

146444

146446

146448

146449

146457

146458

146459

146465

146466

146475

146478

146488

146489

146490

146499

146501

146505

146506

146508

146516

146517

146518

146519

146521

146522

146533

146535

146536

146537

146539

146540

146557

146561

146563

146568

146569

146571

146573

146574

146575

146576

146578

146579

146586

146587

146588

146595

146598

146600

146607

146613

146614

146615

146617

146618

146619

146620

146621

146622

146624

146628

146629

146635

146637

146638

146639

146650

146656

146661

146663

146664

146666

146667

146669

146670

146672

146673

146678

146683

146684

146686

146687

146696

146697

146698

146701

146702

146726

146729

146730

146738

146751

146753

146756

146757

146764

146765

146767

146778

146780

146806

146811

146812

146816

146817

146818

146838

146839

146851

146853

146854

146855

146856

146857

146858

146860

146863

146864

146865

146866

146870

146877

146878

146879

146880

146881

146887

146901

146905

146907

146908

146923

146925

146936

146938

146939

146951

146952

146953

146954

146955

146972

146974

146977

146980

146984

146987

146989

147005

147008

147022

147024

147037

147038

147039

147040

147042

147043

147044

147045

147046

147048

147060

147069

147072

147074

147076

147077

147080

147082

147083

147084

147085

147086

147087

147088

147089

147090

147100

147104

147123

147124

147125

147127

147128

147131

147141

147148

147154

147155

147157

147160

147161

147162

147164

147165

147169

147170

147178

147179

147190

147191

147192

147196

147197

147233

147234

147236

147238

147240

147269

147277

147279

147280

147287

147288

147289

147300

147303

147308

147309

147310

147317

147318

147320

147321

147323

147333

147334

147337

147364

147367

147368

147372

147373

147403

147424

147425

147426

147429

147430

147431

147433

147435

147436

147445

147448

147451

147467

147468

147469

147471

147474

147486

147493

147496

147511

147523

147524

147525

147528

147547

147564

147566

147567

147570

147575

147576

147577

147586

147587

147598

147600

147602

147603

147615

147627

147629

147641

147642

147646

147667

147668

147676

147692

147695

147696

147709

147710

147712

147728

147729

147752

147753

147755

147757

147761

147763

147764

147788

147789

147796

147820

147821

147824

147825

147836

147849

147864

147869

147882

147883

147887

147907

147916

147917

147923

147924

147925

147946

147956

147975

147988

147992

147994

148012

148021

148023

148025

148027

148036

148045

148056

148058

148060

148061

148066

148067

148068

148069

148070

148088

148089

148098

148100

148114

148130

148133

148134

148136

148152

148155

148157

148162

148164

148180

148186

148188

148189

148190

148191

148196

148201

148221

148224

148235

148240

148255

148290

148291

148292

148294

'''

# 单独下载章节
jm_photos = '''



'''


def env(name, default, trim=('[]', '""', "''")):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default

    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]

    return value


def parse_id_items(val):
    if not val:
        return set()
    if isinstance(val, (list, tuple, set)):
        res = set()
        for item in val:
            res.update(parse_id_items(str(item)))
        return res
    if not isinstance(val, str):
        val = str(val)
    res = set()
    for line in val.replace(',', '\n').splitlines():
        line = line.split('#', 1)[0].strip()
        if line:
            res.add(line)
    return res


def get_id_set(env_name, given):
    aid_set = set()
    aid_set.update(parse_id_items(given))
    env_val = env(env_name, '').replace('-', '\n')
    aid_set.update(parse_id_items(env_val))
    return aid_set


def extract_ids_from_text(source: str):
    """
    从源码文本中提取 jm_albums 和 jm_photos 的配置
    """
    import ast
    import re

    albums_str, photos_str = '', ''

    def ast_to_str(val_node):
        if val_node is None:
            return ''
        if isinstance(val_node, ast.Constant):
            return str(val_node.value)
        if isinstance(val_node, (ast.List, ast.Tuple, ast.Set)):
            return '\n'.join(str(e.value) for e in val_node.elts if isinstance(e, ast.Constant))
        return ''

    try:
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == 'jm_albums':
                            albums_str = ast_to_str(node.value)
                        elif target.id == 'jm_photos':
                            photos_str = ast_to_str(node.value)
    except Exception:
        pass

    if not albums_str:
        m = re.search(r"jm_albums\s*=\s*('''|\"\"\")(.*?)\1", source, re.DOTALL)
        if m:
            albums_str = m.group(2)
    if not photos_str:
        m = re.search(r"jm_photos\s*=\s*('''|\"\"\")(.*?)\1", source, re.DOTALL)
        if m:
            photos_str = m.group(2)

    return albums_str, photos_str


def get_id_set_from_git():
    """
    当工作区脚本被上游同步覆盖时，尝试从当前 git commit (HEAD) 自动恢复用户在 commit 中填写的 ID
    """
    import subprocess
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        res = subprocess.run(
            ['git', 'show', 'HEAD:usage/workflow_download.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            cwd=script_dir
        )
        if res.returncode == 0 and res.stdout:
            return extract_ids_from_text(res.stdout)
    except Exception:
        pass
    return '', ''


def format_file_size(size):
    if size >= 1024 * 1024:
        return f'{size / 1024 / 1024:.2f}MB'
    return f'{size / 1024:.1f}KB'


class WorkflowCompressionStats:

    def __init__(self):
        self.lock = Lock()
        self.image_count = 0
        self.original_size = 0
        self.final_size = 0

    def record(self, original_size, final_size):
        with self.lock:
            self.image_count += 1
            self.original_size += original_size
            self.final_size += final_size

    def snapshot(self):
        with self.lock:
            return self.image_count, self.original_size, self.final_size


def compress_image_in_place(filepath, quality, convert_to_jpeg=False):
    target_path = filepath
    temp_path = f'{filepath}.jmcomic-compress.tmp'
    original_size = os.path.getsize(filepath)

    try:
        with Image.open(filepath) as image:
            image_format = image.format
            image_info = image.info.copy()
            save_kwargs = {}

            if getattr(image, 'n_frames', 1) > 1:
                return image_format, None, None, False, filepath, 'multi_frame'

            if convert_to_jpeg and image_format in {'PNG', 'WEBP'}:
                image_format = 'JPEG'
                target_path = os.path.splitext(filepath)[0] + '.jpg'
                if image.mode not in {'RGB', 'L'}:
                    if image.mode in {'RGBA', 'LA'} or 'transparency' in image_info:
                        image = image.convert('RGBA')
                        background = Image.new('RGB', image.size, 'white')
                        background.paste(image, mask=image.getchannel('A'))
                        image = background
                    else:
                        image = image.convert('RGB')
                save_kwargs.update(quality=quality, optimize=True)
            elif image_format in {'JPEG', 'JPG'}:
                save_kwargs.update(quality=quality, optimize=True)
            elif image_format == 'WEBP':
                save_kwargs.update(quality=quality)
            elif image_format == 'PNG':
                return image_format, None, None, False, filepath, 'unsupported_format'
            else:
                return image_format, None, None, False, filepath, 'unsupported_format'

            for key in ('exif', 'icc_profile'):
                value = image_info.get(key)
                if value is not None:
                    save_kwargs[key] = value

            image.save(temp_path, format=image_format, **save_kwargs)

        compressed_size = os.path.getsize(temp_path)
        if target_path == filepath and compressed_size >= original_size:
            os.remove(temp_path)
            return image_format, original_size, compressed_size, False, filepath, None

        os.replace(temp_path, target_path)
        if target_path != filepath:
            os.remove(filepath)

        return image_format, original_size, compressed_size, True, target_path, None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


class WorkflowImageCompressPlugin(JmOptionPlugin):
    plugin_key = 'workflow_image_compress'

    def invoke(self, image, quality, stats, convert_to_jpeg=False, **kwargs):
        old_path = image.save_path
        image_format, original_size, compressed_size, replaced, new_path, skip_reason = compress_image_in_place(
            old_path,
            quality,
            convert_to_jpeg,
        )

        if skip_reason == 'multi_frame':
            self.log(f'跳过多帧图片压缩以保留动画: {image_format}, {old_path}')
            return

        if original_size is None:
            self.log(f'跳过不支持质量压缩的图片格式: {image_format}, {old_path}')
            return

        if new_path != old_path:
            image.save_path = new_path

        final_size = compressed_size if replaced else original_size
        stats.record(original_size, final_size)
        compression_ratio = original_size / final_size
        action = '压缩完成' if replaced else '压缩后未变小，保留原图'
        self.log(
            f'{action}: {new_path}, '
            f'{format_file_size(original_size)} → {format_file_size(final_size)}, '
            f'压缩比 {compression_ratio:.2f}:1'
        )


class WorkflowImageCompressSummaryPlugin(JmOptionPlugin):
    plugin_key = 'workflow_image_compress_summary'

    def invoke(self, stats, **kwargs):
        image_count, original_size, final_size = stats.snapshot()
        if image_count == 0:
            self.log('压缩汇总: 没有可压缩的图片')
            return

        compression_ratio = original_size / final_size
        compression_rate = (original_size - final_size) / original_size * 100
        self.log(
            f'压缩汇总: 共处理 {image_count} 张图片, '
            f'{format_file_size(original_size)} → {format_file_size(final_size)}, '
            f'总压缩比 {compression_ratio:.2f}:1, 总压缩率 {compression_rate:.1f}%'
        )


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS', jm_albums)
    photo_id_set = get_id_set('JM_PHOTO_IDS', jm_photos)

    # 兜底恢复：若本地变量与环境变量均未指定任何 ID，尝试从 git commit (HEAD) 自动恢复
    if len(album_id_set) == 0 and len(photo_id_set) == 0:
        git_albums, git_photos = get_id_set_from_git()
        if git_albums:
            album_id_set.update(parse_id_items(git_albums))
        if git_photos:
            photo_id_set.update(parse_id_items(git_photos))
        if len(album_id_set) > 0 or len(photo_id_set) > 0:
            jm_log('workflow', f'检测到工作区脚本被上游同步覆盖，已自动从 commit (HEAD) 恢复下载配置: '
                               f'album={list(album_id_set)}, photo={list(photo_id_set)}')

    # 防御性校验：若仍没有任何 ID，直接报错阻断，避免生成 247B 空压缩包误导用户
    if len(album_id_set) == 0 and len(photo_id_set) == 0:
        if env('GITHUB_REPOSITORY', '') == env('UPSTREAM_REPO', 'hect0x7/JMComic-Crawler-Python'):
            jm_log('workflow', '主仓库未配置任何本子或章节 ID，跳过下载')
            return

        ExceptionTool.raises(
            '未配置任何本子或章节 ID！请在 usage/workflow_download.py 中填写 jm_albums / jm_photos，'
            '或在 GitHub Actions 中配置环境变量 JM_ALBUM_IDS / JM_PHOTO_IDS。'
        )

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')


def get_option():
    # 读取 option 配置文件
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_workflow_download.yml')))

    # 支持工作流覆盖配置文件的配置
    cover_option_config(option)

    # 把请求错误的html下载到文件，方便GitHub Actions下载查看日志
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new

    impl = env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)

    pdf_option = env('PDF_OPTION', None)
    convert_to_jpeg = bool(pdf_option and pdf_option != '否')

    try:
        image_quality = int(env('IMAGE_QUALITY', '100'))
    except ValueError:
        ExceptionTool.raises('IMAGE_QUALITY 必须是1到100之间的整数')

    ExceptionTool.require_true(
        1 <= image_quality <= 100,
        'IMAGE_QUALITY 必须是1到100之间的整数'
    )

    if image_quality < 100:
        compression_stats = WorkflowCompressionStats()
        JmModuleConfig.register_plugin(WorkflowImageCompressPlugin)
        JmModuleConfig.register_plugin(WorkflowImageCompressSummaryPlugin)
        option.plugins.setdefault('after_image', []).append({
            'plugin': WorkflowImageCompressPlugin.plugin_key,
            'kwargs': {
                'quality': image_quality,
                'convert_to_jpeg': convert_to_jpeg,
                'stats': compression_stats,
            },
        })
        option.plugins.setdefault('after_download', []).append({
            'plugin': WorkflowImageCompressSummaryPlugin.plugin_key,
            'kwargs': {
                'stats': compression_stats,
            },
        })

    if pdf_option and pdf_option != '否':
        call_when = 'after_album' if pdf_option == '是 | 本子维度合并pdf' else 'after_photo'
        
        pdf_name_rule = env('PDF_NAME_RULE', None)
        if isinstance(pdf_name_rule, str):
            pdf_name_rule = pdf_name_rule.strip()
            
        if not pdf_name_rule:
            pdf_name_rule = '[JM{Aid}] {Atitle}' if call_when == 'after_album' else '[JM{Aid}] 第{Pindex}章-JM{Pid}-{Ptitle}'
            
        plugin = [{
            'plugin': Img2pdfPlugin.plugin_key,
            'kwargs': {
                'pdf_dir': option.dir_rule.base_dir + '/pdf/',
                'filename_rule': pdf_name_rule,
                'delete_original_file': True,
            }
        }]
        option.plugins[call_when] = plugin


def log_before_raise():
    jm_download_dir = env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    def decide_filepath(e):
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)

        if resp is None:
            suffix = str(time_stamp())
        else:
            suffix = resp.url

        name = '-'.join(
            fix_windir_name(it)
            for it in [
                e.description,
                current_thread().name,
                suffix
            ]
        )

        path = f'{jm_download_dir}/【出错了】{name}.log'
        return path

    def exception_listener(e: JmcomicException):
        """
        异常监听器，实现了在 GitHub Actions 下，把请求错误的信息下载到文件，方便调试和通知使用者
        """
        # 决定要写入的文件路径
        path = decide_filepath(e)

        # 准备内容
        content = [
            str(type(e)),
            e.msg,
        ]
        for k, v in e.context.items():
            content.append(f'{k}: {v}')

        # resp.text
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)
        if resp:
            content.append(f'响应文本: {resp.text}')

        # 写文件
        write_text(path, '\n'.join(content))

    JmModuleConfig.register_exception_listener(JmcomicException, exception_listener)


if __name__ == '__main__':
    main()
