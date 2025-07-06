import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:google_places_flutter/google_places_flutter.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'dart:math';
import 'dart:convert';
import 'utils.dart';

class LocationGame extends StatefulWidget {
  const LocationGame({super.key});

  @override
  _LocationGameState createState() => _LocationGameState();
}

class _LocationGameState extends State<LocationGame>
    with SingleTickerProviderStateMixin {
  // map
  late GoogleMapController _mapController;
  late final Set<Marker> _markers = {};
  final double _initialZoom = 13.0;
  // Icon
  late BitmapDescriptor _markerIcon;
  final String _myLocationIconLeft = 'assets/location_game-user_icon1.png';
  final String _myLocationIconRight = 'assets/location_game-user_icon2.png';
  // destination
  final List<Map<String, dynamic>> _destinations = [
    {'name': '渋谷駅', 'location': LatLng(35.658033, 139.701635)},
    {'name': '東京タワー', 'location': LatLng(35.6585805, 139.7454329)},
    {'name': 'スカイツリー', 'location': LatLng(35.710063, 139.810700)},
    {'name': '大阪城', 'location': LatLng(34.687300, 135.525900)},
    {'name': 'Hareza Tower', 'location': LatLng(35.7324188, 139.7152077)},
    {'name': '富士山', 'location': LatLng(35.2139, 138.4339)},
    {'name': '利尻島', 'location': LatLng(45.1286111, 141.1805555)},
    {'name': '佐渡島', 'location': LatLng(37.8533333, 138.3205555)},
    {'name': '小豆島', 'location': LatLng(34.5033333, 134.2413888)},
    {'name': '硫黄島', 'location': LatLng(30.7822222, 130.2791666)},
    {'name': '奄美大島', 'location': LatLng(28.3202777, 129.5322222)},
    {'name': '西表島', 'location': LatLng(24.4191666, 123.7777777)},
    {'name': '井の頭公園', 'location': LatLng(35.7, 139.5744444)},
    {'name': '兼六園', 'location': LatLng(36.5619444, 136.6619444)},
    {'name': '嵐山', 'location': LatLng(35.0108333, 135.6791666)},
    {'name': '造幣局', 'location': LatLng(34.6966666, 135.5208333)},
    {'name': '舞鶴公園', 'location': LatLng(38.3555555, 140.3761111)},
    {'name': '六本木ヒルズ', 'location': LatLng(35.6602777, 139.7291666)},
    {'name': 'ランドマークタワー', 'location': LatLng(35.4544444, 139.6313888)},
    {'name': '朱鷺メッセ', 'location': LatLng(37.9258333, 139.0597222)},
    {'name': '比叡山ドライブウエイ', 'location': LatLng(35.0513888, 135.8386111)},
    {'name': '黄金山', 'location': LatLng(34.3672222, 132.4905555)},
    {'name': '福岡タワー', 'location': LatLng(33.5933333, 130.3513888)},
    {'name': '弘前城', 'location': LatLng(40.6075, 140.4638888)},
    {'name': '盛岡城', 'location': LatLng(39.7005555, 141.15)},
    {'name': '仙台城（青葉城）', 'location': LatLng(38.2530555, 140.8555555)},
    {'name': '会津若松城', 'location': LatLng(37.4875, 139.9297222)},
    {'name': '水戸城', 'location': LatLng(36.3752777, 140.4769444)},
    {'name': '小田原城', 'location': LatLng(35.2513888, 139.1536111)},
    {'name': '松本城', 'location': LatLng(36.2386111, 137.9688888)},
    {'name': '金沢城', 'location': LatLng(36.5636111, 136.6594444)},
    {'name': '名古屋城', 'location': LatLng(35.1858333, 136.8994444)},
    {'name': '彦根城', 'location': LatLng(35.2763888, 136.2516666)},
    {'name': '安土城', 'location': LatLng(35.1558333, 136.1391666)},
    {'name': '二条城', 'location': LatLng(35.0141666, 135.7477777)},
    {'name': '大阪城', 'location': LatLng(34.6875, 135.5258333)},
    {'name': '姫路城', 'location': LatLng(34.8394444, 134.6938888)},
    {'name': '松山城', 'location': LatLng(33.8455555, 132.7655555)},
    {'name': '宇和島城', 'location': LatLng(33.2191666, 132.565)},
    {'name': '首里城', 'location': LatLng(26.2169444, 127.7194444)},
    {'name': '五稜郭跡', 'location': LatLng(41.79722222, 140.7569444)},
    {'name': '三内丸山遺跡', 'location': LatLng(40.81138889, 140.6966667)},
    {'name': '多賀城跡', 'location': LatLng(38.30666667, 140.9883333)},
    {'name': '秋田城跡', 'location': LatLng(39.74083333, 140.0811111)},
    {'name': '白水阿弥陀堂', 'location': LatLng(37.03611111, 140.8372222)},
    {'name': '虎塚古墳', 'location': LatLng(36.37388889, 140.5694444)},
    {'name': '富岡製糸場', 'location': LatLng(36.25527778, 138.8875)},
    {'name': '岩宿遺跡', 'location': LatLng(36.4, 139.2875)},
    {'name': '埼玉古墳群', 'location': LatLng(36.12694444, 139.4791667)},
    {'name': '上総国分尼寺跡', 'location': LatLng(35.49972222, 140.1180556)},
    {'name': '湯島聖堂', 'location': LatLng(35.70055556, 139.7669444)},
    {'name': '大森貝塚', 'location': LatLng(35.59083333, 139.7291667)},
    {'name': '佐渡金山遺跡', 'location': LatLng(38.04194444, 138.2591667)},
    {'name': '関ヶ原古戦場', 'location': LatLng(35.36777778, 136.4655556)},
    {'name': '登呂遺跡', 'location': LatLng(34.95583333, 138.4080556)},
    {'name': '北条氏史跡', 'location': LatLng(35.04638889, 138.9372222)},
    {'name': '清水寺', 'location': LatLng(34.99472222, 135.785)},
    {'name': '龍河洞', 'location': LatLng(33.60277778, 133.7452778)},
    {'name': '吉野ヶ里遺跡', 'location': LatLng(33.32555556, 130.3841667)},
    {'name': '平戸和蘭商館跡', 'location': LatLng(33.37222222, 129.5569444)},
    {'name': '斎場御嶽', 'location': LatLng(26.17333333, 127.8272222)},
  ];
  LatLng _currentPosition = LatLng(35.681236, 139.767125); // 初期位置（東京駅）
  String? _currentDestinationName;
  LatLng? _currentDestinationLocation;
  double? _currentDestinationDistance;
  double? _cullentDestinationBearing;
  String? _currentDisplayDistance;
  final double goalDistance = 500; // 500mまで近づいたらゴール
  bool _isGoal = false;
  bool _isLoading = false;
  String _loadingMessage = '';
  bool _isMapCreated = false;
  // roulette
  late AnimationController _controller;
  late Animation<double> _animation;
  bool _isSpinning = false;
  double _arrowAngle = 0.0;
  // ramen
  final String _mapsApiKey = dotenv.env['GOOGLE_MAPS_API_KEY'] ?? '';
  final String _placesApiKey = dotenv.env['GOOGLE_PLACES_API_KEY'] ?? '';
  var _nearByRamenShop = {};
  bool _isOpenRamenModal = false;
  int _stepCount = 0;
  bool _isDispDestDistance = false; // 目的地までの距離を表示するか（最初はなし）
  bool _isDispDestBearing = false; // 目的地の方角を表示するか（最初はなし）

  @override
  void initState() {
    super.initState();
    _loadMarkerIcon(_myLocationIconLeft);
    _controller = AnimationController(
      vsync: this,
      duration: Duration(seconds: 2), // 2秒で1周
    )..addListener(() {
        setState(() {
          _arrowAngle = _controller.value * 2 * pi; // 0〜360度を回転
        });
      });

    _animation = Tween<double>(begin: 0, end: 1).animate(_controller);
  }

  // 画像を読み込む
  Future<void> _loadMarkerIcon(iconPath) async {
    _markerIcon = await BitmapDescriptor.fromAssetImage(
      const ImageConfiguration(size: Size(48, 48), devicePixelRatio: 2.5),
      iconPath,
    );
  }

  // 地図が作成された後の動作
  void _onMapCreated(GoogleMapController controller) async {
    _mapController = controller;
    // 目的地の設定とマーカーの設定
    _setTargetDestination(_currentDestinationName);
    // 中央位置にマーカーを設定する
    _setCenterMarker();
    // 地図の用意が完了
    setState(() {
      _isMapCreated = true;
    });
  }

  // 目的地の設定とマーカーの設定
  void _setTargetDestination(currentDest) async {
    final targetDest = randomChoice(_destinations);
    if (targetDest['name'] == currentDest) {
      _setTargetDestination(currentDest);
    } else {
      setState(() {
        _currentDestinationName = targetDest['name'];
        _currentDestinationLocation = targetDest['location'];
        _currentDestinationDistance =
            _calculateDistance(_currentPosition, _currentDestinationLocation!);
        _cullentDestinationBearing =
            _calculateBearing(_currentPosition, _currentDestinationLocation!);
        _currentDisplayDistance = _displayDistance(_currentDestinationDistance);

        double zoom = _calculateZoom(_currentDestinationDistance);
        _mapController
            .animateCamera(CameraUpdate.newLatLngZoom(_currentPosition, zoom));
        _markers.add(Marker(
          markerId: MarkerId(_currentDestinationName!),
          position: _currentDestinationLocation!,
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
        ));
        // 目的地までのヒントを削除
        _stepCount = 0;
        _isDispDestDistance = false;
        _isDispDestBearing = false;
      });
    }
  }

  // 2点間の距離を計算 (メートル)
  double _calculateDistance(LatLng from, LatLng to) {
    return Geolocator.distanceBetween(
      from.latitude,
      from.longitude,
      to.latitude,
      to.longitude,
    );
  }

  // 2点間の角度を計算（0-360）
  double _calculateBearing(LatLng from, LatLng to) {
    // 返される角度は0〜360度の範囲で、0度が北、90度が東、180度が南、270度が西を示します。
    return Geolocator.bearingBetween(
      from.latitude,
      from.longitude,
      to.latitude,
      to.longitude,
    );
  }

  // 距離の表示
  String _displayDistance(double? distance) {
    if (distance == null) return '';
    if (_isGoal) return 'ゴール !!';

    // 距離に応じてkm/m表記を変える
    if (distance > 2000) {
      return '距離: ${(distance / 1000).toStringAsFixed(2)} km';
    } else {
      return '距離: ${distance.toStringAsFixed(2)} m';
    }
  }

  // ズーム倍率の計算
  double _calculateZoom(double? distance) {
    if (distance == null) return 12.0;

    if (distance < 1_000) {
      return 15.0;
    } else if (distance < 2_000) {
      return 14.0;
    } else if (distance < 5_000) {
      return 13.0;
    } else if (distance < 10_000) {
      return 12.0;
    } else if (distance < 20_000) {
      return 11.0;
    } else if (distance < 50_000) {
      return 10.0;
    } else {
      return 9.0;
    }
  }

  // 中央位置にマーカーを設定する
  void _setCenterMarker() async {
    LatLngBounds bounds = await _mapController.getVisibleRegion();
    LatLng center = LatLng(
      (bounds.northeast.latitude + bounds.southwest.latitude) / 2,
      (bounds.northeast.longitude + bounds.southwest.longitude) / 2,
    );

    setState(() {
      _markers.add(Marker(
        markerId: MarkerId('center_marker'),
        position: center,
        icon: _markerIcon,
      ));
    });
  }

  // カメラ移動時の動作
  void _onCameraMove(CameraPosition position) {
    setState(() {
      _markers.add(Marker(
        markerId: MarkerId('center_marker'),
        position: position.target, // カメラの中央位置
        icon: _markerIcon,
      ));
    });
  }

  // 左右の方向でアイコンを変える
  void changeMyLocationIcon(LatLng from, LatLng to) {
    if (to.longitude < from.longitude) {
      _loadMarkerIcon(_myLocationIconLeft);
    } else {
      _loadMarkerIcon(_myLocationIconRight);
    }
  }

  // サイコロアイコン押下時
  void _roulette() async {
    // ゴール中の場合
    if (_isGoal) {
      setState(() {
        _isGoal = false;
      });
      // 次の目的地を設定
      _setTargetDestination(_currentDestinationName);
      return;
    }
    // ルーレットが回っている場合
    if (_isSpinning) {
      // ルーレットをストップ
      _controller.stop();

      // 矢印の方向のランダムな位置を取得
      LatLng randomPosition = _moveInDirection(_arrowAngle);

      // 移動
      _changePosition(randomPosition);
      _stepCount++;
      setState(() {
        _isDispDestDistance = _stepCount >= 1;
        _isDispDestBearing = _stepCount >= 2;
      });
    } else {
      _controller.repeat();
    }

    setState(() {
      _isSpinning = !_isSpinning;
    });
    return;
  }

  // 方位を元にランダムで進む先のpositionを設定
  LatLng _moveInDirection(double angle) {
    // ランダムな距離を決定（目的地までの0.5倍～1.5倍までがランダムで決定）
    double distance = randomInRange(
        _currentDestinationDistance! * 0.5, _currentDestinationDistance! * 1.2);
    double distanceInDegrees = distance / 111320; // 1度 ≈ 111.32km

    // 進む方向を計算
    double newLat = _currentPosition.latitude + distanceInDegrees * cos(angle);
    double newLng = _currentPosition.longitude + distanceInDegrees * sin(angle);
    LatLng newPosition = LatLng(newLat, newLng);

    return newPosition;
  }

  // 移動
  void _changePosition(LatLng newPosition,
      {double? forceZoom, bool isNoGoalMoving = false}) async {
    // カメラを移動
    changeMyLocationIcon(_currentPosition, newPosition);
    double distance =
        _calculateDistance(newPosition, _currentDestinationLocation!);
    double zoom = _calculateZoom(distance);
    // 強制ズームがONの場合
    if (forceZoom != null) {
      zoom = forceZoom;
    }
    await _mapController.animateCamera(
      CameraUpdate.newLatLngZoom(newPosition, zoom),
    );

    setState(() {
      // 現在地を更新
      _currentPosition = newPosition;
      // 目的地までの距離を更新
      _currentDestinationDistance = distance;
      // ゴール判定
      if (!isNoGoalMoving) {
        _isGoal = _checkGoal(_currentDestinationDistance);
      }
      // 目的地までの方角を更新
      _cullentDestinationBearing =
          _calculateBearing(_currentPosition, _currentDestinationLocation!);
      // 画面表示内容を取得
      _currentDisplayDistance = _displayDistance(_currentDestinationDistance);
      // ゴール時は目的地まで移動する
      if (!isNoGoalMoving && _isGoal) {
        _mapController.animateCamera(
          CameraUpdate.newLatLngZoom(_currentDestinationLocation!, 18),
        );
        _currentPosition = _currentDestinationLocation!;
        // 1/2でラーメンを探す
        // if (randomBool()) {
        //   _fetchNearbyRamenShop(_currentPosition);
        // }
      }
    });
  }

  // ゴールしたかどうかを判定
  bool _checkGoal(double? distance) {
    if (distance == null) {
      return false;
    }
    if (distance < goalDistance) {
      return true;
    }
    return false;
  }

  // 現在地アイコン押下時
  void _onPressMyLocation() async {
    // 権限をリクエスト
    LocationPermission permission = await Geolocator.requestPermission();

    if (permission == LocationPermission.always ||
        permission == LocationPermission.whileInUse) {
      setState(() {
        _loadingMessage = '現在地に移動しています...';
        _isLoading = true;
      });
      // 現在地を取得
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high, // 高精度で取得
      );
      LatLng latLng = LatLng(position.latitude, position.longitude);

      // 移動
      _changePosition(latLng);

      // ロード中表示を解除
      setState(() {
        _isLoading = false;
      });
    }
  }

  // 指定位置近くのラーメンショップを検索
  Future<void> _fetchNearbyRamenShop(LatLng position,
      {int radius = 100}) async {
    setState(() {
      _loadingMessage = 'ラーメン屋を探しています...';
      _isLoading = true;
    });
    // 現在位置地を取得
    double latitude = position.latitude;
    double longitude = position.longitude;

    // Google Places APIのエンドポイント
    final String url =
        "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        "?location=$latitude,$longitude"
        "&language=ja"
        "&radius=$radius" // 半径100m以内
        "&type=restaurant" // レストランを検索
        "&keyword=ラーメン屋" // キーワード "ラーメン"
        "&key=$_placesApiKey";

    // APIリクエストを送信
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      List<dynamic> results = data['results'];
      // 0件の場合
      if (results.isEmpty) {
        if (radius < 10000) {
          setState(() {
            _loadingMessage = '広範囲のラーメン屋を探しています...';
          });
          _fetchNearbyRamenShop(position, radius: radius * 10);
        }
        // ロード中表示を解除
        setState(() {
          _isLoading = false;
        });
        return;
      }
      // 1件を取得して表示
      var shop = randomChoice(results);
      shop['radiusText'] = '(検索範囲: 半径 $radius m以内)';
      setState(() {
        _nearByRamenShop = shop;
        _isOpenRamenModal = true;
      });
    } else {
      print("APIエラー: ${response.statusCode}");
      // ロード中表示を解除
      setState(() {
        _isLoading = false;
      });
    }
  }

  // URLを開く
  Future<void> _launchURL(String url) async {
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      throw 'Could not launch $url';
    }
  }

  // 画面レイアウト
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Location Game'),
        leading: IconButton(
          icon: Icon(Icons.arrow_back), // 戻るアイコン
          onPressed: () {
            Navigator.pop(context); // トップページに戻る
          },
        ),
      ),
      body: Stack(children: [
        // 地図レイヤ
        GoogleMap(
          initialCameraPosition: CameraPosition(
            target: _currentPosition,
            zoom: _initialZoom,
          ),
          markers: _markers,
          onMapCreated: _onMapCreated,
          onCameraMove: _onCameraMove,
          myLocationEnabled: false, // 現在地機能を利用しない
          scrollGesturesEnabled: true, // スクロール無効
          zoomGesturesEnabled: false, // ズーム無効
          zoomControlsEnabled: true,
          rotateGesturesEnabled: false, // 回転無効
          tiltGesturesEnabled: false, // 傾き無効
        ),
        // 目的地の情報表示レイヤ
        if (_currentDestinationName != null &&
            _currentDisplayDistance != null) ...[
          Positioned(
            top: MediaQuery.of(context).size.height * 0.1 + 20, // 画面の1/4の位置
            left: 20,
            right: 20,
            child: Stack(
              children: [
                Container(
                    padding: EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.6), // 半透明背景
                      borderRadius: BorderRadius.circular(10),
                    ),
                    alignment: Alignment.center,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          "目的地: $_currentDestinationName",
                          style: TextStyle(color: Colors.white, fontSize: 18),
                        ),
                        SizedBox(height: 3),
                        Text(
                          _isDispDestDistance
                              ? _currentDisplayDistance!
                              : '距離: ????km',
                          style: TextStyle(color: Colors.white, fontSize: 16),
                        ),
                      ],
                    )),
                !_isGoal &&
                        _cullentDestinationBearing != null &&
                        _isDispDestBearing
                    ? Positioned(
                        top: 12,
                        left: 20,
                        child: Transform.rotate(
                          angle: (_cullentDestinationBearing! - 90) *
                              pi /
                              180, // ラジアンに変換
                          child: Icon(
                            Icons.arrow_forward,
                            size: 50,
                            color: const Color.fromARGB(200, 255, 255, 255),
                          ),
                        ))
                    : SizedBox.shrink(),
              ],
            ),
          )
        ],
        // 現在位置情報ボタン
        Positioned(
          top: 20,
          right: 80,
          child: SizedBox(
              width: 48,
              height: 48,
              child: FloatingActionButton(
                heroTag: "myLocation",
                onPressed: _onPressMyLocation,
                backgroundColor: const Color.fromARGB(127, 81, 83, 85),
                child: Icon(Icons.my_location, size: 24, color: Colors.white),
              )),
        ),
        // ラーメン検索ボタン
        Positioned(
          top: 20,
          right: 20,
          child: SizedBox(
              width: 48,
              height: 48,
              child: FloatingActionButton(
                heroTag: "ramenSearch",
                onPressed: () => _fetchNearbyRamenShop(_currentPosition),
                backgroundColor: const Color.fromARGB(127, 81, 83, 85),
                child: Icon(Icons.ramen_dining, size: 24, color: Colors.white),
              )),
        ),
        // サイコロボタン
        Positioned(
            bottom: 20,
            left: 0,
            right: 0,
            child: Align(
                alignment: Alignment.center,
                child: SizedBox(
                  width: 96,
                  height: 84,
                  child: FloatingActionButton(
                    heroTag: "roulette",
                    onPressed: _roulette,
                    tooltip: 'Are you LUCKY??',
                    backgroundColor: _isSpinning
                        ? const Color.fromARGB(168, 243, 33, 82)
                        : const Color.fromARGB(168, 33, 150, 243),
                    child: Icon(_isSpinning ? Icons.stop : Icons.casino,
                        size: 50, color: Colors.white),
                  ),
                ))),
        // 回転矢印ボタン
        if (_isMapCreated) ...[
          Positioned(
              top: MediaQuery.of(context).size.height / 2 - 40,
              left: MediaQuery.of(context).size.width / 2 - 25,
              child: Transform.rotate(
                  angle: _arrowAngle,
                  child: Icon(
                    Icons.keyboard_double_arrow_up,
                    size: 50,
                    color: const Color.fromARGB(222, 201, 43, 43),
                  )))
        ],
        // オーバーレイとローディングアイコン（最上段）
        if (_isLoading) ...[
          // 背景を薄い黒にする
          Container(
            color: const Color.fromARGB(180, 0, 0, 0),
            width: double.infinity,
            height: double.infinity,
          ),
          // アイコンを画面中央に配置
          Stack(
            children: [
              Positioned(
                  top: MediaQuery.of(context).size.height / 2, // 少し上
                  left: 0,
                  right: 0,
                  child: Center(
                      child: Text(
                    _loadingMessage,
                    style: TextStyle(color: Colors.white, fontSize: 18),
                  ))),
              Center(
                child: CupertinoActivityIndicator(
                  radius: 32,
                  color: Colors.white,
                ), // ローディングアイコン
              )
            ],
          ),
        ],
        _nearByRamenShop != {} && _isOpenRamenModal
            ? Container(
                child: AnimatedPadding(
                  padding: EdgeInsets.all(20), // モーダルの周りに余白を設定
                  duration: Duration(milliseconds: 300), // アニメーションの時間
                  curve: Curves.easeInOut, // アニメーションの曲線
                  child: Center(
                    child: Container(
                      width: 300, // 幅200px
                      height: 350, // 高さ200px
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16), // 角丸
                        boxShadow: [
                          BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 10)
                        ],
                      ),
                      child: Stack(children: [
                        // 右上の閉じるボタン
                        Positioned(
                          top: 10,
                          right: 10,
                          child: IconButton(
                            icon: Icon(Icons.close),
                            onPressed: () {
                              setState(() {
                                _isLoading = false;
                                _isOpenRamenModal = false;
                              }); // モーダルを閉じる
                            },
                          ),
                        ),
                        Center(
                            child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            // テキスト情報
                            Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.center,
                                children: [
                                  Text(
                                    'ラーメン屋が見つかりました',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  SizedBox(height: 4),
                                  Text(
                                    "${_nearByRamenShop['radiusText']}",
                                    style:
                                        TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                  SizedBox(height: 16),
                                  Text(
                                    "${_nearByRamenShop['name']}",
                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  SizedBox(height: 8),
                                  Text(
                                    "評価: ${_nearByRamenShop['rating'].toStringAsFixed(1)}",
                                    style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold),
                                  ),
                                  SizedBox(height: 16),
                                  Text(
                                    "${_nearByRamenShop['vicinity']}",
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  SizedBox(height: 8),
                                  TextButton(
                                    style: ButtonStyle(
                                      backgroundColor: WidgetStateProperty.all(
                                          Colors.blue), // 背景色
                                      foregroundColor: WidgetStateProperty.all(
                                          Colors.white), // 文字色
                                    ),
                                    onPressed: () {
                                      // お店に移動
                                      setState(() {
                                        _isOpenRamenModal = false;
                                        _isLoading = false;
                                      });
                                      LatLng latLng = LatLng(
                                          _nearByRamenShop['geometry']
                                              ['location']['lat'],
                                          _nearByRamenShop['geometry']
                                              ['location']['lng']);
                                      _changePosition(latLng,
                                          forceZoom: 18, isNoGoalMoving: true);
                                    },
                                    child: Text(
                                      "　この店に行く!!　",
                                      style: TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                  TextButton(
                                    onPressed: () {
                                      // GoogleMapへのリンクを開く処理
                                      String url =
                                          "https://www.google.com/maps/place/?q=place_id:${_nearByRamenShop['place_id']}";
                                      print(
                                          "ID: ${_nearByRamenShop['place_id']}, url: $url");
                                      _launchURL(url);
                                    },
                                    child: Text(
                                      "GoogleMapでお店を見る",
                                      style: TextStyle(color: Colors.blue),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        )),
                      ]),
                    ),
                  ),
                ),
              )
            : SizedBox.shrink(),
      ]),
    );
  }
}
