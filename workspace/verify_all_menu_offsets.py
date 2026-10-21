import struct

bin_path = r'D:\Game\dragon quest heroes i & ii\romfs\dqh2\LINKDATA.BIN'
idx_path = r'D:\Game\dragon quest heroes i & ii\romfs\dqh2\LINKDATA.IDX'

with open(idx_path, 'rb') as f:
    idx = f.read()

off_22, sz_22, _, _ = struct.unpack_from('<QQQQ', idx, 22 * 32)
off_36, sz_36, _, _ = struct.unpack_from('<QQQQ', idx, 36 * 32)

with open(bin_path, 'rb') as f:
    f.seek(off_22)
    e22 = f.read(sz_22)
    f.seek(off_36)
    e36 = f.read(sz_36)

checks_e36 = [
    (86990, '冒険をする'),
    (87006, '冒険の書をつくる'),
    (87031, '冒険の書を消す'),
    (87066, 'プレイ時間'),
    (87082, '記録日時'),
    (87095, 'ストーリー'),
    (87111, '使用していません'),
    (6512,  '何番の冒険の書を　作りますか？'),
    (87361, '主人公の名前を　決めてください。'),
    (88634, 'そうび'),
    (88624, 'スキル'),
    (88644, 'もちもの'),
    (88657, 'つよさ'),
    (88667, 'アクション一覧'),
    (88689, 'せんれき'),
    (88702, 'さくせん'),
    (88715, '時空の書'),
    (88728, 'ルーラ'),
    (88738, 'リレミト'),
    (88751, 'おわかれのつばさ'),
    (85140, '買いにきた'),
    (85156, '売りにきた'),
    (87724, 'おいのりをする'),
    (87746, '冒険をやめる'),
    (87887, 'アクセサリーを　強化する'),
    (87924, 'アクセサリーを　解体する'),
    (88088, '鑑定する'),
    (88459, '交換する'),
    (88569, 'クエストを受ける'),
    (88776, 'スキルふりわけ'),
    (88798, 'とくぎ・じゅもんつけかえ'),
    (88835, 'パーティスキルつけかえ'),
    (97469, '転職する'),
    (97482, 'スキルポイントをふりなおす'),
    (98143, 'クエストを報告する'),
    (90206, 'システム設定'),
    (90225, 'カメラ設定'),
    (90241, 'ボリューム設定'),
    (90174, 'そうさ方法'),
    (90190, 'マニュアル'),
    (90383, 'オートセーブ'),
    (90402, 'ネットワーク接続'),
    (90427, 'そうさタイプ'),
    (90500, 'コントローラー振動'),
    (90528, '必殺技演出の短縮'),
    (90553, 'ダメージ表示'),
    (90572, '操作ガイド表示'),
    (90594, '初期設定に戻す'),
    (85067, 'はい'),
    (85074, 'いいえ'),
    (85377, 'はずす'),
    (86087, 'けってい'),
    (86243, 'やめる'),
    (88472, 'キープする'),
    (88488, 'キープをやめる'),
]

checks_e22 = [
    (632, '教会'),
    (641, '武器屋'),
    (653, 'オーブ屋'),
    (668, 'メダル王'),
    (683, 'クエスト所'),
    (701, '錬金屋'),
    (713, 'ルイーダ'),
    (728, 'リッカ'),
    (740, '転職所'),
    (752, '表彰所'),
    (764, '討伐報告所'),
    (782, '交換所'),
    (818, '師範'),
]

print('=== Buffer checks Entry 36 ===')
for off, exp in checks_e36:
    end = e36.find(b'\x00', off)
    buf_size = end - off + 1
    # also check if there are trailing nulls
    trail = 0
    while end + trail + 1 < len(e36) and e36[end + trail + 1] == 0:
        trail += 1
    total_avail = buf_size + trail
    print(f'E36 @ {off:6d}: {exp:30s} -> len {len(exp.encode("utf-8")):2d}, total_avail {total_avail:2d}')

print('=== Buffer checks Entry 22 ===')
for off, exp in checks_e22:
    end = e22.find(b'\x00', off)
    buf_size = end - off + 1
    trail = 0
    while end + trail + 1 < len(e22) and e22[end + trail + 1] == 0:
        trail += 1
    total_avail = buf_size + trail
    print(f'E22 @ {off:6d}: {exp:30s} -> len {len(exp.encode("utf-8")):2d}, total_avail {total_avail:2d}')
