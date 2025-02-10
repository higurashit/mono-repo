import 'package:flutter/material.dart';
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
  LatLng _currentPosition = LatLng(35.681236, 139.767125); // 初期位置（東京駅）

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  Future<void> _getCurrentLocation() async {
    var status = await Permission.location.request();
    if (status.isGranted) {
      Position position = await Geolocator.getCurrentPosition();
      setState(() {
        _currentPosition = LatLng(position.latitude, position.longitude);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: GoogleMap(
        initialCameraPosition: CameraPosition(
          target: _currentPosition,
          zoom: 15.0,
        ),
        onMapCreated: (GoogleMapController controller) {
          mapController = controller;
        },
        myLocationEnabled: true, // 現在地マーカーを表示
      ),
    );
  }
}
