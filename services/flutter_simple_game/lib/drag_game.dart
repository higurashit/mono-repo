import 'package:flutter/material.dart';
// import 'dart:developer' as dev;
import 'utils.dart';

class DragGame extends StatelessWidget {
  const DragGame({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: DragBoxExample(),
    );
  }
}

class DragBoxExample extends StatefulWidget {
  const DragBoxExample({super.key});

  @override
  _DragBoxExampleState createState() => _DragBoxExampleState();
}

class _DragBoxExampleState extends State<DragBoxExample> {
  double x = 100;
  double y = 100;
  Color color = Colors.green;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
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
    );
  }
}
