import 'package:flutter/material.dart';
import 'utils.dart';

class SimpleGame extends StatefulWidget {
  const SimpleGame({super.key});

  @override
  _SimpleGameState createState() => _SimpleGameState();
}

class _SimpleGameState extends State<SimpleGame> {
  double ballX = 0.0; // ボールの位置X
  double ballY = 0.0; // ボールの位置Y
  double ballSpeedX = 0.01; // X方向の速度
  double ballSpeedY = 0.01;

  @override
  void initState() {
    super.initState();

    // ゲームの更新処理
    Future.doWhile(() async {
      // 毎フレームごとにボールの位置を更新
      if (mounted) {
        setState(() {
          ballX += ballSpeedX;
          ballY += ballSpeedY;

          // 壁に当たった場合、反射させる
          if (ballX + 0.15 >= 1 || ballX <= -1) {
            ballSpeedX = -ballSpeedX;
            ballSpeedY =
                ballSpeedY + randomInRange(0, 0.01) * randomPlusOrMinus();
            // print("$ballSpeedX $ballSpeedY");
          }
          if (ballY + 0.15 >= 1 || ballY <= -1) {
            ballSpeedY = -ballSpeedY;
            ballSpeedX =
                ballSpeedX + randomInRange(0, 0.01) * randomPlusOrMinus();
            // print("$ballSpeedX $ballSpeedY");
          }
        });
      }
      await Future.delayed(Duration(milliseconds: 16)); // 60fpsに近い更新
      return true;
    });
  }

  void _speedUpCounter() {
    if (mounted) {
      setState(() {
        // This call to setState tells the Flutter framework that something has
        // changed in this State, which causes it to rerun the build method below
        // so that the display can reflect the updated values. If we changed
        // _counter without calling setState(), then the build method would not be
        // called again, and so nothing would appear to happen.
        if (ballSpeedX < 0) {
          ballSpeedX -= 0.01;
        } else {
          ballSpeedX += 0.01;
        }
        if (ballSpeedY < 0) {
          ballSpeedY -= 0.01;
        } else {
          ballSpeedY += 0.01;
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: Text('Simple Game'),
          leading: IconButton(
            icon: Icon(Icons.arrow_back), // 戻るアイコン
            onPressed: () {
              Navigator.pop(context); // トップページに戻る
            },
          ),
        ),
        body: Center(
          child: Container(
            width: 300,
            height: 300,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.black),
            ),
            child: Stack(
              children: [
                Positioned(
                  left: (ballX + 1) * 150, // 画面の中央を基準に位置
                  top: (ballY + 1) * 150,
                  child: Container(
                    width: 20,
                    height: 20,
                    decoration: BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: _speedUpCounter,
          tooltip: 'SpeedUp!!',
          child: const Icon(Icons.add),
        ), // This trailing comma makes auto-formatting nicer for build methods.
      ),
    );
  }
}
