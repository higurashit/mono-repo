import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:math';
import 'utils.dart';

class LocationGame extends StatefulWidget {
  const LocationGame({super.key});

  @override
  _LocationGameState createState() => _LocationGameState();
}

class _LocationGameState extends State<LocationGame> {
  late GoogleMapController mapController;
  late final Set<Marker> _markers = {};
  final double _initialZoom = 13.0;
  late BitmapDescriptor _markerIcon;
  final String _myLocationIconLeft = 'assets/location_game-user_icon1.png';
  final String _myLocationIconRight = 'assets/location_game-user_icon2.png';
  final List<Map<String, dynamic>> _destinations = [
    {'name': '渋谷駅', 'location': LatLng(35.658033, 139.701635)},
    {'name': '東京タワー', 'location': LatLng(35.6585805, 139.7454329)},
    {'name': 'スカイツリー', 'location': LatLng(35.710063, 139.810700)},
    {'name': '大阪城', 'location': LatLng(34.687300, 135.525900)},
  ];
  LatLng _currentPosition = LatLng(35.681236, 139.767125); // 初期位置（東京駅）
  String? _currentDestinationName;
  LatLng? _currentDestinationLocation;
  double? _currentDestinationDistance;
  double? _cullentDestinationBearing;
  String? _currentDisplayDistance;
  // final int _durationMilliseconds = 100;
  bool _isGoal = true;
  bool _isLoading = false;

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
  void _onMapCreated(GoogleMapController controller) async {
    mapController = controller;
    // 目的地の設定とマーカーの設定
    _setTargetDestination(_currentDestinationName);
    // 中央位置にマーカーを設定する
    _setCenterMarker();
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
        mapController
            .animateCamera(CameraUpdate.newLatLngZoom(_currentPosition, zoom));
        _markers.add(Marker(
          markerId: MarkerId(_currentDestinationName!),
          position: _currentDestinationLocation!,
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
        ));
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
    _isGoal = false;
    if (distance == null) {
      return '';
    } else if (distance > 2000) {
      return '距離: ${(distance / 1000).toStringAsFixed(2)} km';
    } else if (distance > 500) {
      return '距離: ${distance.toStringAsFixed(2)} m';
    } else {
      _isGoal = true;
      return 'ゴール !!';
    }
  }

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
    if (_isGoal) {
      _setTargetDestination(_currentDestinationName);
      return;
    }
    // ランダムな位置にマーカーを追加
    int ratio = (_currentDestinationDistance! / 2000).toInt();
    if (ratio < 1) {
      ratio = 1;
    }
    LatLng randomPosition = getNearRandomLatLng(
      _currentPosition,
      _currentDestinationLocation!,
      ratio: ratio,
    );
    // カメラを移動
    changeMyLocationIcon(_currentPosition, randomPosition);
    double distance =
        _calculateDistance(randomPosition, _currentDestinationLocation!);
    double zoom = _calculateZoom(distance);
    await mapController.animateCamera(
      CameraUpdate.newLatLngZoom(randomPosition, zoom),
    );
    setState(() {
      _currentPosition = randomPosition;
      _currentDestinationDistance = distance;
      _cullentDestinationBearing =
          _calculateBearing(_currentPosition, _currentDestinationLocation!);
      _currentDisplayDistance = _displayDistance(_currentDestinationDistance);
      // ゴール時
      if (_isGoal) {
        mapController.animateCamera(
          CameraUpdate.newLatLngZoom(_currentDestinationLocation!, 18),
        );
        _currentPosition = _currentDestinationLocation!;
      }
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
      double distance = _calculateDistance(_currentPosition, latLng);
      double zoom = _calculateZoom(distance);
      await mapController.animateCamera(
        CameraUpdate.newLatLngZoom(latLng, zoom),
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
        // 目的地の情報表示
        if (_currentDestinationName != null &&
            _currentDisplayDistance != null) ...[
          Positioned(
            top: MediaQuery.of(context).size.height * 0.1, // 画面の1/4の位置
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
                          _currentDisplayDistance!,
                          style: TextStyle(color: Colors.white, fontSize: 16),
                        ),
                      ],
                    )),
                !_isGoal && _cullentDestinationBearing != null
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
        // 位置情報ボタン
        Positioned(
          top: 20,
          right: 20,
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
        // サイコロボタン
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
        // オーバーレイとローディングアイコン
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
