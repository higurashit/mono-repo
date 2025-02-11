import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'utils.dart';

class LocationGame extends StatefulWidget {
  const LocationGame({super.key});

  @override
  _LocationGameState createState() => _LocationGameState();
}

class _LocationGameState extends State<LocationGame> {
  late GoogleMapController mapController;
  LatLng _currentPosition = LatLng(35.681236, 139.767125); // 初期位置（東京駅）
  late Set<Marker> _markers = {};
  late BitmapDescriptor _markerIcon;
  bool _isLoading = false;
  final int _durationMilliseconds = 100;
  final String _myLocationIconLeft = 'assets/location_game-user_icon1.png';
  final String _myLocationIconRight = 'assets/location_game-user_icon2.png';
  final List<Map<String, dynamic>> destinations = [
    {'name': '渋谷駅', 'location': LatLng(35.658033, 139.701635)},
    {'name': '東京タワー', 'location': LatLng(35.6585805, 139.7454329)},
    {'name': 'スカイツリー', 'location': LatLng(35.710063, 139.8107)},
    {'name': '大阪城', 'location': LatLng(34.6873, 135.5259)},
  ];

  @override
  void initState() {
    super.initState();
    _loadMarkerIcon(_myLocationIconLeft);
  }

  // 画像を読み込む
  Future<void> _loadMarkerIcon(iconPath) async {
    _markerIcon = await BitmapDescriptor.fromAssetImage(
      const ImageConfiguration(size: Size(48, 48), devicePixelRatio: 2.5),
      iconPath,
    );
  }

  // 地図が作成された後の動作
  void _onMapCreated(GoogleMapController controller) {
    mapController = controller;
    _setCenterMarker();
  }

  // 中央位置にマーカーを設定する
  void _setCenterMarker() async {
    LatLngBounds bounds = await mapController.getVisibleRegion();
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
      _markers = {
        Marker(
          markerId: MarkerId('center_marker'),
          position: position.target, // カメラの中央位置
          icon: _markerIcon,
        ),
      };
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
    // ランダムな位置にマーカーを追加
    LatLng randomPosition = getRandomLatLng(
      position: _currentPosition,
      ratio: 5,
    );
    changeMyLocationIcon(_currentPosition, randomPosition);
    // カメラを移動
    await mapController.animateCamera(
      CameraUpdate.newLatLng(randomPosition),
    );
    setState(() {
      _currentPosition = randomPosition;
    });
  }

  // 現在地アイコン押下時
  void _onPressMyLocation() async {
    // 権限をリクエスト
    LocationPermission permission = await Geolocator.requestPermission();

    if (permission == LocationPermission.always ||
        permission == LocationPermission.whileInUse) {
      setState(() {
        _isLoading = true;
      });
      // 現在地を取得
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high, // 高精度で取得
      );
      LatLng latLng = LatLng(position.latitude, position.longitude);

      // カメラを移動
      changeMyLocationIcon(_currentPosition, latLng);
      await mapController.animateCamera(
        CameraUpdate.newLatLng(latLng),
      );
      setState(() {
        _currentPosition = latLng;
        _isLoading = false;
      });
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
        GoogleMap(
          initialCameraPosition: CameraPosition(
            target: _currentPosition,
            zoom: 13.0,
          ),
          markers: _markers,
          onMapCreated: _onMapCreated,
          onCameraMove: _onCameraMove,
          myLocationEnabled: false, // 現在地機能を利用しない
          scrollGesturesEnabled: false, // スクロール無効
          zoomGesturesEnabled: false, // ズーム無効
          zoomControlsEnabled: false,
          rotateGesturesEnabled: false, // 回転無効
          tiltGesturesEnabled: false, // 傾き無効
        ),
        Positioned(
          top: 20, // 上から20ピクセル
          right: 20, // 右から20ピクセル
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
        Positioned(
            bottom: 20,
            left: 0,
            right: 0,
            child: Align(
                alignment: Alignment.center,
                child: SizedBox(
                  width: 64,
                  height: 56,
                  child: FloatingActionButton(
                    heroTag: "roulette",
                    onPressed: _roulette,
                    tooltip: 'Are you LUCKY??',
                    backgroundColor: const Color.fromARGB(222, 33, 150, 243),
                    child:
                        const Icon(Icons.casino, size: 32, color: Colors.white),
                  ),
                ))),
        // オーバーレイとアイコン
        if (_isLoading) ...[
          // 背景を薄い黒にする
          Container(
            color: const Color.fromARGB(180, 0, 0, 0),
            width: double.infinity,
            height: double.infinity,
          ),
          // アイコンを画面中央に配置
          Center(
            child: CupertinoActivityIndicator(
              radius: 32,
              color: Colors.white,
            ), // ローディングアイコン
          ),
        ],
      ]),
    );
  }
}
