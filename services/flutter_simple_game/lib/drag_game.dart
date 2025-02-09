import 'package:flutter/material.dart';
// import 'dart:developer' as dev;
import 'utils.dart';

class DragGame extends StatefulWidget {
  const DragGame({super.key});

  @override
  _DragGameState createState() => _DragGameState();
}

class _DragGameState extends State<DragGame> {
  double x = 100;
  double y = 100;
  Color color = Colors.green;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        home: Scaffold(
      appBar: AppBar(
        title: Text('Drag Game'),
        leading: IconButton(
          icon: Icon(Icons.arrow_back), // 戻るアイコン
          onPressed: () {
            Navigator.pop(context); // トップページに戻る
          },
        ),
      ),
      body: Stack(
        children: [
          Positioned(
            left: x,
            top: y,
            child: GestureDetector(
              onPanUpdate: (details) {
                setState(() {
                  x += details.delta.dx;
                  y += details.delta.dy;
                  color = Color.fromARGB(255, randomIntInRange(0, 255),
                      randomIntInRange(0, 255), randomIntInRange(0, 255));
                });
              },
              child: Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ),
        ],
      ),
    ));
  }
}
