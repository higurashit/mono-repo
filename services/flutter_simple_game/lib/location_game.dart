import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter/services.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
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
      body: GoogleMap(
        initialCameraPosition: CameraPosition(
          target: _currentPosition,
          zoom: 14.0,
        ),
        markers: _markers,
        onMapCreated: _onMapCreated,
        onCameraMove: _onCameraMove,
        myLocationEnabled: true, // 現在地マーカーを表示
      ),
    );
  }
}
