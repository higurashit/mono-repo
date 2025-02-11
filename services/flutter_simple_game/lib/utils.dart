import 'dart:math' as math;
import 'package:google_maps_flutter/google_maps_flutter.dart';

var rand = math.Random();

double randomInRange(double min, double max) {
  return min + rand.nextDouble() * (max - min);
}

int randomIntInRange(int min, int max) {
  return min + rand.nextInt(max - min + 1);
}

int randomIntInArray(List<int> arr) {
  return arr[rand.nextInt(arr.length)];
}

int randomPlusOrMinus() {
  return randomIntInArray([1, -1]);
}

bool randomBool() {
  return randomChoice([true, false]);
}

randomChoice(List arr) {
  int length = arr.length;
  // 要素が0, 1の場合
  if (length == 0) return null;
  if (length == 1) return arr[0];
  // 要素が2以上の場合
  int target = randomIntInRange(0, length - 1);
  return arr[target];
}

// ランダムな位置を取得する
LatLng getRandomLatLng(LatLng position, {int ratio = 1}) {
  double randomLat =
      position.latitude + (rand.nextDouble() - 0.5) * 0.01 * ratio;
  double randomLng =
      position.longitude + (rand.nextDouble() - 0.5) * 0.01 * ratio;
  // print("position : $position");
  // print("randomLat: $randomLat, randomLng: $randomLng");
  return LatLng(randomLat, randomLng);
}

// ターゲットに近づけるようなランダムな位置を取得する
LatLng getNearRandomLatLng(LatLng position, LatLng target, {int ratio = 1}) {
  int latitudeFactor = 1;
  int longitudeFactor = 1;
  if (target.latitude < position.latitude) {
    latitudeFactor = -1;
  }
  if (target.longitude < position.longitude) {
    longitudeFactor = -1;
  }
  double randomLat = position.latitude +
      (rand.nextDouble() / 0.5) * 0.01 * ratio * latitudeFactor;
  double randomLng = position.longitude +
      (rand.nextDouble() / 0.5) * 0.01 * ratio * longitudeFactor;
  // print("position : $position");
  // print("randomLat: $randomLat, randomLng: $randomLng");
  return LatLng(randomLat, randomLng);
}
