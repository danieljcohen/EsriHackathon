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
    return (
      <video controls width="250">
        <source src="/media/daniel.webm" type="video/webm" />
        <source src="/media/daniel.mp4" type="video/mp4" />
        Download the
        <a href="/media/daniel.webm">WEBM</a>
        or
        <a href="/media/daniel.mp4">MP4</a>
        video.
      </video>
    );
  }

  // --------------------------------------------------------------------------
  //
  //  Private methods
  //
  // --------------------------------------------------------------------------
}
