import { Component, Element, h, VNode } from '@stencil/core';
import '@esri/calcite-components';
// import Map from '@esri/Map';
// import MapView from '@esri/views/MapView';
// import VideoLayer from '@esri/layers/VideoLayer';
// import VideoPlayer from '@esri/widgets/VideoPlayer';

@Component({
  tag: 'arcgis-asset-tracker-panel',
  styleUrl: 'arcgis-asset-tracker-panel.scss',
  shadow: true,
})
export class ArcgisAssetTrackerPanel {
  @Element() hostElement: ArcgisAssetTrackerPanel;

  //--------------------------------------------------------------------------
  //
  //  Properties
  //
  //--------------------------------------------------------------------------

  //--------------------------------------------------------------------------
  //
  //  Private Properties
  //
  //--------------------------------------------------------------------------

  //--------------------------------------------------------------------------
  //
  //  Lifecycle
  //
  //--------------------------------------------------------------------------

  componentWillLoad(): void {}

  // --------------------------------------------------------------------------
  //
  //  Renderer methods
  //
  // --------------------------------------------------------------------------

  render(): VNode {
    return <div class="video-player"></div>;
  }

  // --------------------------------------------------------------------------
  //
  //  Private methods
  //
  // --------------------------------------------------------------------------
}
