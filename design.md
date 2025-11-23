# Api-key:
8603efb746f84156ac23dc6c01f2cde1
5036288716b24b36963ef12593226613
eb8128a358004dfc8ac18ffec9c49641
17fa085ddb9549b5902c57c424a3f196
25d2964215dc4a4cbb27ccfdec13cf60
455ccc56007c410d98134e512febf499
e787c7a24bb748ae9e6c3509dbfad0f0
e3be792da99d407a97b3b99581e26fdb
f50a167f98dc481782aa64f2cd41ff91
e01ad8f36a3b4aaba7e2bc7f0568945a
36b3056df26f492e996faf84bb95e298
937d94ad977d4c6e8ba45cf263bd7e2f
5f87f269ef4e453aae4657d564d52180
3d300fb080ae44e698c5c66dfb0da558
ffdb21b912db47b0879c0590144188d6
b35c503e2e924aa1bec3ebac31678370
d9b6563eec4242d18c17171ec9205361
be0da64416d9412699fe330ae436a340
dae26c804c014f41ac6a5ef1e4c6e55e
9213080bb155478e86e2cae1c6b29c92
035bb0c4d44f4540ad7ef92f595a541c
75071e8964754d2d8d9044c8d0740128
3485ba70a1034a38973d72323bcb40f7
56e26c09d47f4b79a21edf15adab9f8c
628893788c7043bbb6c70891c29284b4
a264e9e7b3024cb5b0cb4d45f196064a
91f7aca98367432588fe6364e049e434
6bf05b48271241d1937f7c298b2ae635
74f2210f9db14318b249e3d82d0ccca7
393f4370ebfe48f198adf7cd22257173
ae4d1653abe543559b98b02a8344da1a
e88b88351e85427cbea20498ffc4c2d3

## API-key管理器
首先根据https://doc.steamdt.com/6369437m0，中的说明文档，我们知道不同的调用方法的限制
url	备注	权限
/open/cs2/v1/wear	通过检视链接查询磨损度相关数据	每小时36000次
/open/cs2/v2/wear	通过ASMD参数查询磨损度相关数据	每小时36000次
/open/cs2/v1/inspect	通过检视链接生成检视图,前提是已经获取到饰品的磨损度	每日100次
/open/cs2/v2/inspect	通过ASMD参数生成检视图,前提是已经获取到饰品的磨损度	每日100次
/open/cs2/v1/price/single	通过marketHashName查询饰品价格	每分钟60次
/open/cs2/v1/price/batch	通过marketHashName批量查询饰品价格	每分钟1次
/open/cs2/v1/base	获取steam饰品基础信息	每日1次

我的设想是设计一个可以轻松获取数据的类，原型是当我用xx命令调用它的时候（暂时只设计open/cs2/v1/price/single）这一个命令，argment是marketHashName（string）；管理器会创建一个线程，根据当前管理器记录的每个api-key哪个还有剩余额度，然后分配它过去获取数据，剩余额度的数据暂时采用内存文件csv储存：记录当前分钟（GST+8），每个api-key在这个分钟剩余的额度；

## single饰品爬取的数据
{'success': True, 'data': [{'platform': 'SKINPORT', 'platformItemId': '', 'sellPrice': 0, 'sellCount': 0, 'biddingPrice': 0, 'biddingCount': 0, 'updateTime': 1756742400}, {'platform': 'YOUPIN', 'platformItemId': '58399', 'sellPrice': 47.85, 'sellCount': 16, 'biddingPrice': 16.3, 'biddingCount': 3, 'updateTime': 1763904902}, {'platform': 'BUFF', 'platformItemId': '41530', 'sellPrice': 35.0, 'sellCount': 19, 'biddingPrice': 23.1, 'biddingCount': 3, 'updateTime': 1763904901}, {'platform': 'STEAM', 'platformItemId': '', 'sellPrice': 29.59, 'sellCount': 15, 'biddingPrice': 0.0, 'biddingCount': 0, 'updateTime': 1763902345}, {'platform': 'HALOSKINS', 'platformItemId': '18717357', 'sellPrice': 77.48, 'sellCount': 6, 'biddingPrice': 0.0, 'biddingCount': 0, 'updateTime': 1763901722}, {'platform': 'C5', 'platformItemId': '18717357', 'sellPrice': 75.0, 'sellCount': 6, 'biddingPrice': 0.0, 'biddingCount': 0, 'updateTime': 1763906463}, {'platform': 'CSMONEY', 'platformItemId': '', 'sellPrice': 0, 'sellCount': 0, 'biddingPrice': 0, 'biddingCount': 0, 'updateTime': 1751385600}, {'platform': 'WAXPEER', 'platformItemId': '', 'sellPrice': 0, 'sellCount': 0, 'biddingPrice': 0, 'biddingCount': 0, 'updateTime': 1756742400}, {'platform': 'DMARKET', 'platformItemId': '', 'sellPrice': 0, 'sellCount': 0, 'biddingPrice': 0, 'biddingCount': 0, 'updateTime': 1752508800}], 'errorCode': 0, 'errorMsg': None, 'errorData': None, 'errorCodeStr': None}