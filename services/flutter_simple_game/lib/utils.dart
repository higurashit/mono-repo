import 'dart:math' as math;
import 'package:health/health.dart';
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

// IOS
/// List of data types available on iOS
const List<HealthDataType> dataTypesIOS = [
  HealthDataType.ACTIVE_ENERGY_BURNED,
  HealthDataType.AUDIOGRAM,
  HealthDataType.BASAL_ENERGY_BURNED,
  HealthDataType.BLOOD_GLUCOSE,
  HealthDataType.BLOOD_OXYGEN,
  HealthDataType.BLOOD_PRESSURE_DIASTOLIC,
  HealthDataType.BLOOD_PRESSURE_SYSTOLIC,
  HealthDataType.BODY_FAT_PERCENTAGE,
  HealthDataType.BODY_MASS_INDEX,
  HealthDataType.BODY_TEMPERATURE,
  HealthDataType.DIETARY_CARBS_CONSUMED,
  HealthDataType.DIETARY_CAFFEINE,
  HealthDataType.DIETARY_ENERGY_CONSUMED,
  HealthDataType.DIETARY_FATS_CONSUMED,
  HealthDataType.DIETARY_PROTEIN_CONSUMED,
  HealthDataType.ELECTRODERMAL_ACTIVITY,
  HealthDataType.FORCED_EXPIRATORY_VOLUME,
  HealthDataType.HEART_RATE,
  HealthDataType.HEART_RATE_VARIABILITY_SDNN,
  HealthDataType.HEIGHT,
  HealthDataType.RESPIRATORY_RATE,
  HealthDataType.PERIPHERAL_PERFUSION_INDEX,
  HealthDataType.STEPS,
  HealthDataType.WAIST_CIRCUMFERENCE,
  HealthDataType.WEIGHT,
  HealthDataType.FLIGHTS_CLIMBED,
  HealthDataType.DISTANCE_WALKING_RUNNING,
  HealthDataType.MINDFULNESS,
  HealthDataType.SLEEP_AWAKE,
  HealthDataType.SLEEP_ASLEEP,
  HealthDataType.SLEEP_IN_BED,
  HealthDataType.SLEEP_LIGHT,
  HealthDataType.SLEEP_DEEP,
  HealthDataType.SLEEP_REM,
  HealthDataType.WATER,
  HealthDataType.EXERCISE_TIME,
  HealthDataType.WORKOUT,
  HealthDataType.HEADACHE_NOT_PRESENT,
  HealthDataType.HEADACHE_MILD,
  HealthDataType.HEADACHE_MODERATE,
  HealthDataType.HEADACHE_SEVERE,
  HealthDataType.HEADACHE_UNSPECIFIED,
  HealthDataType.LEAN_BODY_MASS,

  // note that a phone cannot write these ECG-based types - only read them
  // HealthDataType.ELECTROCARDIOGRAM,
  // HealthDataType.HIGH_HEART_RATE_EVENT,
  // HealthDataType.IRREGULAR_HEART_RATE_EVENT,
  // HealthDataType.LOW_HEART_RATE_EVENT,
  // HealthDataType.RESTING_HEART_RATE,
  // HealthDataType.WALKING_HEART_RATE,
  // HealthDataType.ATRIAL_FIBRILLATION_BURDEN,

  HealthDataType.NUTRITION,
  HealthDataType.GENDER,
  HealthDataType.BLOOD_TYPE,
  HealthDataType.BIRTH_DATE,
  HealthDataType.MENSTRUATION_FLOW,
  HealthDataType.WATER_TEMPERATURE,
  HealthDataType.UNDERWATER_DEPTH,
];

/// List of data types available on Android.
///
/// Note that these are only the ones supported on Android's Health Connect API.
/// Android's Health Connect has more types that we support in the [HealthDataType]
/// enumeration.
const List<HealthDataType> dataTypesAndroid = [
  HealthDataType.ACTIVE_ENERGY_BURNED,
  HealthDataType.BASAL_ENERGY_BURNED,
  HealthDataType.BLOOD_GLUCOSE,
  HealthDataType.BLOOD_OXYGEN,
  HealthDataType.BLOOD_PRESSURE_DIASTOLIC,
  HealthDataType.BLOOD_PRESSURE_SYSTOLIC,
  HealthDataType.BODY_FAT_PERCENTAGE,
  HealthDataType.HEIGHT,
  HealthDataType.WEIGHT,
  HealthDataType.LEAN_BODY_MASS,
  // HealthDataType.BODY_MASS_INDEX,
  HealthDataType.BODY_TEMPERATURE,
  HealthDataType.HEART_RATE,
  HealthDataType.HEART_RATE_VARIABILITY_RMSSD,
  HealthDataType.STEPS,
  HealthDataType.DISTANCE_DELTA,
  HealthDataType.RESPIRATORY_RATE,
  HealthDataType.SLEEP_ASLEEP,
  HealthDataType.SLEEP_AWAKE_IN_BED,
  HealthDataType.SLEEP_AWAKE,
  HealthDataType.SLEEP_DEEP,
  HealthDataType.SLEEP_LIGHT,
  HealthDataType.SLEEP_OUT_OF_BED,
  HealthDataType.SLEEP_REM,
  HealthDataType.SLEEP_UNKNOWN,
  HealthDataType.SLEEP_SESSION,
  HealthDataType.WATER,
  HealthDataType.WORKOUT,
  HealthDataType.RESTING_HEART_RATE,
  HealthDataType.FLIGHTS_CLIMBED,
  HealthDataType.NUTRITION,
  HealthDataType.TOTAL_CALORIES_BURNED,
  HealthDataType.MENSTRUATION_FLOW,
];
