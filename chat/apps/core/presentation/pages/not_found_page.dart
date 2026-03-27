import 'package:flutter/material.dart';
import 'package:hoav2/core/common_widgets/common_elevated_button.dart';
import 'package:hoav2/core/common_widgets/common_image.dart';
import 'package:hoav2/core/common_widgets/common_text.dart';
import 'package:hoav2/core/constant/app_assets.dart';
import 'package:hoav2/core/constant/app_colors.dart';
import 'package:hoav2/core/constant/app_insets.dart';
import 'package:hoav2/core/constant/app_sizes.dart';
import 'package:hoav2/core/extensions/context_extension.dart';
import 'package:hoav2/core/extensions/double_extension.dart';

class NotFoundPage extends StatelessWidget {
const NotFoundPage({ super.key });

  @override
  Widget build(BuildContext context){
    return Scaffold(
      backgroundColor: AppColors.primaryColor,
      body: Center(
        child: Column(
          children: <Widget>[
            CommonImage(
              image: AssetImage(AppAssets.notFound),
              width: context.width,
              height: context.height / 1.5,
            ),
            CommonText(
              text: "PAGE NOT FOUND",
              fontWeight: FontWeight.bold,
              fontSize: AppSizes.font32,
              letterSpacing: AppSizes.size2,
            ),
            CommonText(
              text: "The page you're looking for is not found.",
              letterSpacing: AppSizes.size2,
              fontSize: AppSizes.font16,
              maxLine: 8,
            ),
            AppSizes.size16.height(),
            CommonElevatedButton(
              onButtonPressed: () => context.pop(),
              text: "Go Back",
              width: context.width / 3.5,
              fontColor: AppColors.secondaryColor,
              elevatedPadding: AppInsets.hv8,
            )
          ]
        )
      )
    );
  }
}