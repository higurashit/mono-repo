import 'package:flutter/material.dart';
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
  final LatLng _currentPosition = LatLng(35.681236, 139.767125); // 初期位置（東京駅）
  late Set<Marker> _markers = {};
  late BitmapDescriptor _markerIcon;

  @override
  void initState() {
    super.initState();
    _loadMarkerIcon();
  }

  // 画像を読み込む
  Future<void> _loadMarkerIcon() async {
    _markerIcon = await BitmapDescriptor.fromAssetImage(
      const ImageConfiguration(size: Size(48, 48), devicePixelRatio: 2.5),
      'assets/location_game-user_icon.png',
    );
    setState(() {});
  }

  // 地図が作成された後、中央位置を取得してマーカーを追加
  void _onMapCreated(GoogleMapController controller) {
    mapController = controller;
    _setCenterMarker();
  }

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

  void _roulette() async {
    // ランダムな位置にマーカーを追加
    LatLng randomPosition = getRandomLatLng(
      position: _currentPosition,
      ratio: 5,
    );
    // カメラを移動
    await mapController.animateCamera(
      CameraUpdate.newLatLng(randomPosition),
    );
    // マーカーを移動
    setState(() {
      _markers = {
        Marker(
          markerId: MarkerId('random_marker'),
          position: randomPosition,
          icon: _markerIcon,
        )
      };
    });
  }

  Future<void> _onPressMyLocation() async {
    // 権限をリクエスト
    LocationPermission permission = await Geolocator.requestPermission();

    if (permission == LocationPermission.always ||
        permission == LocationPermission.whileInUse) {
      // 現在地を取得
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high, // 高精度で取得
      );
      LatLng latLng = LatLng(position.latitude, position.longitude);

      // カメラを移動
      await mapController.animateCamera(
        CameraUpdate.newLatLng(latLng),
      );

      // マーカーを移動
      setState(() {
        _markers = {
          Marker(
            markerId: MarkerId('random_marker'),
            position: latLng,
            icon: _markerIcon,
          )
        };
      });
    }
  }

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
        body: Stack(
          children: [
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
                    mini: true,
                    onPressed: _onPressMyLocation,
                    backgroundColor: const Color.fromARGB(127, 81, 83, 85),
                    child:
                        Icon(Icons.my_location, size: 24, color: Colors.white),
                  )),
            ),
          ],
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: _roulette,
          tooltip: 'Are you LUCKY??',
          backgroundColor: Colors.blue,
          child: const Icon(Icons.casino, size: 32, color: Colors.white),
        ),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat);
  }
}
