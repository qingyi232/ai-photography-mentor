"""
AI摄影导师 - 案例库数据
三个分类：构图优良、有待改进、特殊案例，各20张在线图片
图片来源：Unsplash（免费高质量摄影图片）
"""

# 构图优良：明显符合经典构图规则（三分法、对称、引导线、框架式等），整体视觉平衡
EXCELLENT_CASES = [
    {"name": "山脉日出·三分法", "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=75", "desc": "主体位于三分线交点，天空与山脉比例协调"},
    {"name": "湖面倒影·对称", "url": "https://images.unsplash.com/photo-1439853949127-fa647821eba0?w=600&q=75", "desc": "水面完美对称倒影，上下均衡"},
    {"name": "林间小路·引导线", "url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600&q=75", "desc": "道路形成强引导线，视线自然延伸"},
    {"name": "古典建筑·对称", "url": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=600&q=75", "desc": "建筑中轴线对称，庄重大气"},
    {"name": "海岸日落·三分法", "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=75", "desc": "地平线位于下三分线，天空色彩丰富"},
    {"name": "花田纵深·引导线", "url": "https://images.unsplash.com/photo-1490750967868-88aa4f44baee?w=600&q=75", "desc": "花田行列形成纵深引导线"},
    {"name": "桥梁对称·框架", "url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=600&q=75", "desc": "桥梁结构形成框架式构图"},
    {"name": "人像侧面·三分法", "url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&q=75", "desc": "人物位于右三分线，留白方向正确"},
    {"name": "雪山湖泊·黄金比例", "url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&q=75", "desc": "山峰与湖面比例接近黄金分割"},
    {"name": "城市天际线·水平", "url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=600&q=75", "desc": "天际线水平稳定，建筑群节奏感强"},
    {"name": "瀑布长曝·垂直引导", "url": "https://images.unsplash.com/photo-1432405972618-c6b0cfba8b03?w=600&q=75", "desc": "瀑布垂直线条引导视线向下"},
    {"name": "窗框取景·框架式", "url": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=600&q=75", "desc": "自然框架聚焦远景主体"},
    {"name": "沙漠曲线·S形", "url": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=600&q=75", "desc": "沙丘S形曲线优美流畅"},
    {"name": "星空银河·三分法", "url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&q=75", "desc": "银河位于上方三分区域，地景稳定"},
    {"name": "秋叶小径·纵深", "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=75", "desc": "落叶小径形成强烈纵深感"},
    {"name": "教堂穹顶·中心对称", "url": "https://images.unsplash.com/photo-1548625149-fc4a29cf7092?w=600&q=75", "desc": "仰拍穹顶完美中心对称"},
    {"name": "海边栈桥·引导线", "url": "https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=600&q=75", "desc": "栈桥延伸至远方形成引导线"},
    {"name": "田野麦浪·三分法", "url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=600&q=75", "desc": "地平线位于三分线，麦田色彩统一"},
    {"name": "山间公路·曲线引导", "url": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=600&q=75", "desc": "蜿蜒公路形成优美曲线引导"},
    {"name": "日式庭院·均衡", "url": "https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=600&q=75", "desc": "庭院元素分布均衡，视觉重心稳定"},
]

# 有待改进：构图存在明显缺陷，如主体居中、地平线倾斜、画面失衡、背景杂乱等
NEEDS_IMPROVEMENT_CASES = [
    {"name": "主体正中央", "url": "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=600&q=75", "desc": "主体完全居中，缺乏动感和张力"},
    {"name": "地平线居中", "url": "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=600&q=75", "desc": "地平线在正中间，画面缺乏重点"},
    {"name": "背景杂乱", "url": "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=600&q=75", "desc": "背景元素过多，干扰主体表达"},
    {"name": "主体过小", "url": "https://images.unsplash.com/photo-1504567961542-e24d9439a724?w=600&q=75", "desc": "主体在画面中占比过小，不够突出"},
    {"name": "画面倾斜", "url": "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=600&q=75", "desc": "水平线明显倾斜，视觉不稳定"},
    {"name": "顶部空间过多", "url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=600&q=75", "desc": "头顶留白过多，构图不紧凑"},
    {"name": "主体被裁切", "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&q=75", "desc": "主体边缘被不当裁切"},
    {"name": "前景遮挡", "url": "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&q=75", "desc": "前景元素遮挡主体，影响观感"},
    {"name": "光线过曝", "url": "https://images.unsplash.com/photo-1504198453319-5ce911bafcde?w=600&q=75", "desc": "逆光过曝，主体细节丢失"},
    {"name": "元素分散", "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=600&q=75", "desc": "画面元素分散，缺乏视觉焦点"},
    {"name": "色彩混乱", "url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&q=75", "desc": "色彩过于杂乱，缺乏统一色调"},
    {"name": "主体偏边缘", "url": "https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=600&q=75", "desc": "主体过于靠近边缘，画面失衡"},
    {"name": "背景抢眼", "url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600&q=75", "desc": "背景比主体更抢眼，主次不分"},
    {"name": "构图拥挤", "url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=75", "desc": "画面元素过于拥挤，缺乏呼吸感"},
    {"name": "对比度不足", "url": "https://images.unsplash.com/photo-1485470733090-0aae1788d668?w=600&q=75", "desc": "整体灰蒙蒙，主体与背景对比不足"},
    {"name": "视线方向错误", "url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=600&q=75", "desc": "人物视线朝向画面外侧，留白方向反了"},
    {"name": "水平线不平", "url": "https://images.unsplash.com/photo-1473496169904-658ba7c44d8a?w=600&q=75", "desc": "海平面明显倾斜，需要校正"},
    {"name": "主体模糊", "url": "https://images.unsplash.com/photo-1504006833117-8886a355efbf?w=600&q=75", "desc": "对焦不准确，主体不够清晰"},
    {"name": "阴影过重", "url": "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=600&q=75", "desc": "阴影区域过大，暗部细节丢失"},
    {"name": "杂物入镜", "url": "https://images.unsplash.com/photo-1504439468489-c8920d796a29?w=600&q=75", "desc": "边缘有无关杂物入镜，影响整洁度"},
]

# 特殊案例：不符合常规构图规则，但仍具有艺术美感或特殊表达意图
SPECIAL_CASES = [
    {"name": "极简留白", "url": "https://images.unsplash.com/photo-1553949345-eb786bb3f7ba?w=600&q=75", "desc": "大面积留白，极简主义美学，不应按常规评分"},
    {"name": "故意倾斜·荷兰角", "url": "https://images.unsplash.com/photo-1514539079130-25950c84af65?w=600&q=75", "desc": "刻意倾斜营造动感张力，非拍摄失误"},
    {"name": "正中构图·仪式感", "url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=600&q=75", "desc": "主体居中是刻意为之，营造庄重仪式感"},
    {"name": "抽象纹理", "url": "https://images.unsplash.com/photo-1550859492-d5da9d8e45f3?w=600&q=75", "desc": "抽象纹理摄影，无明确主体，重在质感表达"},
    {"name": "剪影逆光", "url": "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=600&q=75", "desc": "故意逆光剪影，牺牲细节换取轮廓美感"},
    {"name": "对角线构图", "url": "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=600&q=75", "desc": "强烈对角线分割画面，打破常规但富有张力"},
    {"name": "高调摄影", "url": "https://images.unsplash.com/photo-1517483000871-1dbf64a6e1c6?w=600&q=75", "desc": "整体高调明亮，故意过曝营造梦幻感"},
    {"name": "低调暗黑", "url": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=600&q=75", "desc": "大面积暗部，低调风格营造神秘氛围"},
    {"name": "微距特写", "url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600&q=75", "desc": "极近距离微距，常规构图规则不完全适用"},
    {"name": "多重曝光", "url": "https://images.unsplash.com/photo-1504700610630-ac6aeefcad02?w=600&q=75", "desc": "多重曝光艺术效果，超越常规构图范畴"},
    {"name": "俯拍平铺", "url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&q=75", "desc": "90度俯拍平铺，对称性评价需特殊考量"},
    {"name": "运动模糊", "url": "https://images.unsplash.com/photo-1461896836934-bd45ba8fcf9b?w=600&q=75", "desc": "故意慢门运动模糊，表达速度感"},
    {"name": "框中框", "url": "https://images.unsplash.com/photo-1494500764479-0c8f2919a3d8?w=600&q=75", "desc": "多层框架嵌套，构图复杂但有层次"},
    {"name": "负空间", "url": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=600&q=75", "desc": "大量负空间包围小主体，极简张力"},
    {"name": "重复图案", "url": "https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=600&q=75", "desc": "重复图案填满画面，韵律感强"},
    {"name": "鱼眼畸变", "url": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=600&q=75", "desc": "鱼眼镜头畸变效果，常规对称分析不适用"},
    {"name": "黑白高对比", "url": "https://images.unsplash.com/photo-1533134486753-c833f0ed4866?w=600&q=75", "desc": "黑白高对比，色彩分析不适用但光影出色"},
    {"name": "全景宽幅", "url": "https://images.unsplash.com/photo-1470770841497-7b3200f18585?w=600&q=75", "desc": "超宽幅全景，常规三分法需调整评价标准"},
    {"name": "倒影错觉", "url": "https://images.unsplash.com/photo-1414609245224-afa02bfb3fda?w=600&q=75", "desc": "水面倒影制造上下颠倒错觉，创意构图"},
    {"name": "光绘长曝", "url": "https://images.unsplash.com/photo-1504893524553-b855bce32c67?w=600&q=75", "desc": "光绘摄影，线条由光源轨迹构成，非常规构图"},
]
